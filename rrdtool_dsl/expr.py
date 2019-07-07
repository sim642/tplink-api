from typing import List, Tuple, Dict


def to_expr(arg):
    if isinstance(arg, Expr):
        return arg
    elif isinstance(arg, int):
        return Const(arg)
    else:
        raise RuntimeError("Unsupported expression")



class ToRefState:
    defs: List["Graphable"]
    expr_vars: Dict["Expr", str]

    def __init__(self) -> None:
        self.fresh_i = 0
        self.defs = []
        self.expr_vars = {}

    def fresh_var(self):
        var = f"var{self.fresh_i}"
        self.fresh_i += 1
        return var


class Expr:
    def to_def(self, var) -> "Def":
        raise NotImplementedError

    always_force_to_ref = False

    def to_ref(self, force: bool, state: ToRefState) -> "Expr":
        self_ref = self.to_ref_inner(state)
        if (force or self.always_force_to_ref) and not isinstance(self_ref, Ref):
            if self in state.expr_vars:
                var = state.expr_vars[self]
            else:
                var = state.fresh_var()
                state.defs.append(self_ref.to_def(var))
                state.expr_vars[self] = var
            return Ref(var)
        else:
            return self_ref

    def to_ref_inner(self, state: ToRefState) -> "Expr":
        raise NotImplementedError

    def to_rpn(self) -> List[str]:
        raise NotImplementedError

    # TODO: add other operators

    def __mul__(self, other) -> "Expr":
        return Binary(self, "*", to_expr(other))

    def __rmul__(self, other) -> "Expr":
        return Binary(to_expr(other), "*", self)


class Rrd(Expr):
    def __init__(self, rrd, name, cf) -> None:
        self.rrd = rrd
        self.name = name
        self.cf = cf

    def __repr__(self) -> str:
        return f"Rrd({self.rrd}, {self.name}, {self.cf})"

    def to_def(self, var) -> "Def":
        return Def(var, self)

    always_force_to_ref = True

    def to_ref_inner(self, state: ToRefState) -> "Expr":
        return self


class Aggregate(Expr):
    expr: Expr

    def __init__(self, expr: Expr, op) -> None:
        self.expr = expr
        self.op = op

    def __repr__(self):
        return f"Aggregate({self.expr}, {self.op})"

    def to_def(self, var) -> "Def":
        return VDef(var, self)

    always_force_to_ref = True

    def to_ref_inner(self, state: ToRefState) -> "Expr":
        expr_ref = self.expr.to_ref(True, state)
        return Aggregate(expr_ref, self.op)

    def to_rpn(self) -> List[str]:
        return self.expr.to_rpn() + [self.op]


class Const(Expr):
    def __init__(self, value) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Const({self.value})"

    def to_def(self, var) -> "Def":
        return VDef(var, self)

    def to_ref_inner(self, state: ToRefState) -> "Expr":
        return self

    def to_rpn(self) -> List[str]:
        return [str(self.value)]


class Binary(Expr):
    left: Expr
    right: Expr

    def __init__(self, left: Expr, op, right: Expr) -> None:
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"Binary({self.left}, {self.op}, {self.right})"

    def to_def(self, var) -> "Def":
        return CDef(var, self)

    def to_ref_inner(self, state: ToRefState) -> "Expr":
        left_ref = self.left.to_ref(False, state)
        right_ref = self.right.to_ref(False, state)
        return Binary(left_ref, self.op, right_ref)

    def to_rpn(self) -> List[str]:
        return self.left.to_rpn() + self.right.to_rpn() + [self.op]


class Ref(Expr):
    def __init__(self, var) -> None:
        self.var = var

    def __repr__(self) -> str:
        return f"Ref({self.var})"

    def to_ref_inner(self, state: ToRefState) -> "Expr":
        return self

    def to_rpn(self) -> List[str]:
        return [self.var]


def as_ref(expr: Expr) -> Ref:
    if isinstance(expr, Ref):
        return expr
    else:
        raise RuntimeError("Not a ref")


class Graphable:
    def to_ref(self, state: ToRefState) -> "Graphable":
        raise NotImplementedError


class DefGraphable(Graphable):
    var: str

    def __init__(self, var: str) -> None:
        self.var = var

    def to_ref(self, state: ToRefState) -> "Graphable":
        return self


class Def(DefGraphable):
    rrd: Rrd

    def __init__(self, var, rrd: Rrd) -> None:
        super().__init__(var)
        self.rrd = rrd

    def __repr__(self) -> str:
        return f"Def({self.var}, {self.rrd})"

    def __str__(self) -> str:
        return f"DEF:{self.var}={self.rrd.rrd}:{self.rrd.name}:{self.rrd.cf}"


class CDef(DefGraphable):
    expr: Expr

    def __init__(self, var, expr: Expr) -> None:
        super().__init__(var)
        self.expr = expr

    def __repr__(self) -> str:
        return f"CDef({self.var}, {self.expr})"

    def __str__(self) -> str:
        return f"CDEF:{self.var}={','.join(self.expr.to_rpn())}"


class VDef(DefGraphable):
    aggregate: Aggregate

    def __init__(self, var, aggregate: Aggregate) -> None:
        super().__init__(var)
        self.aggregate = aggregate

    def __repr__(self) -> str:
        return f"VDef({self.var}, {self.aggregate})"

    def __str__(self) -> str:
        return f"VDEF:{self.var}={','.join(self.aggregate.to_rpn())}"


class Comment(Graphable):
    def __init__(self, text) -> None:
        self.text = text

    def __repr__(self) -> str:
        return f"Comment({self.text})"

    def to_ref(self, state: ToRefState) -> "Graphable":
        return self

    def __str__(self) -> str:
        return f"COMMENT:{self.text}"


class GPrint(Graphable):
    expr: Expr

    def __init__(self, expr: Expr, format) -> None:
        self.expr = expr
        self.format = format

    def __repr__(self) -> str:
        return f"GPrint({self.expr}, {self.format})"

    def to_ref(self, state: ToRefState) -> "Graphable":
        expr_ref = self.expr.to_ref(True, state)
        return GPrint(expr_ref, self.format)

    def __str__(self) -> str:
        return f"GPRINT:{as_ref(self.expr).var}:{self.format}"


class Area(Graphable):
    expr: Expr

    def __init__(self, expr: Expr, color, legend) -> None:
        self.expr = expr
        self.color = color
        self.legend = legend

    def __repr__(self) -> str:
        return f"Area({self.expr}, {self.color}, {self.legend})"

    def to_ref(self, state: ToRefState) -> "Graphable":
        expr_ref = self.expr.to_ref(True, state)
        return Area(expr_ref, self.color, self.legend)

    def __str__(self) -> str:
        return f"AREA:{as_ref(self.expr).var}#{self.color}:{self.legend}"


def outline(graphables: List[Graphable]) -> List[Graphable]:
    to_ref_state = ToRefState()
    ref_graphables = []
    for graphable in graphables:
        ref_graphables.append(graphable.to_ref(to_ref_state))
    return to_ref_state.defs + ref_graphables


if __name__ == '__main__':
    avgbytes = Rrd("thing.rrd", "bytes", "AVERAGE")
    avgbits = avgbytes * 8
    totalavgbits = Aggregate(avgbits, "AVERAGE")

    graphables = [
        Area(avgbits, "00FF00", "Average"),
        GPrint(totalavgbits, "%6.1lf %sbps")
    ]

    for arg in outline(graphables):
        print(f"{arg}")