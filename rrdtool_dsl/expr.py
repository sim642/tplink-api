from typing import List, Tuple, Dict


def exprify(arg):
    if isinstance(arg, Expr):
        return arg
    elif isinstance(arg, int):
        return Const(arg)
    else:
        raise RuntimeError("Unsupported expression")



class RefState:
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
    def refd(self, force: bool, ref_state: RefState) -> "Expr":
        raise RuntimeError("Abstract")

    def __mul__(self, other) -> "Expr":
        return Mul(self, exprify(other))

    def __rmul__(self, other) -> "Expr":
        return Mul(exprify(other), self)


class Rrd(Expr):
    def __init__(self, rrd, name, cf) -> None:
        self.rrd = rrd
        self.name = name
        self.cf = cf

    def __repr__(self) -> str:
        return f"Rrd({self.rrd}, {self.name}, {self.cf})"

    def refd(self, force: bool, ref_state: RefState) -> "Expr":
        if self in ref_state.expr_vars:
            var = ref_state.expr_vars[self]
        else:
            var = ref_state.fresh_var()
            ref_state.defs.append(Def(var, self))
            ref_state.expr_vars[self] = var
        return Ref(var)


class Aggregate(Expr):
    expr: Expr

    def __init__(self, expr: Expr, op) -> None:
        self.expr = expr
        self.op = op

    def __repr__(self):
        return f"Aggregate({self.expr}, {self.op})"

    def refd(self, force: bool, ref_state: RefState) -> "Expr":
        expr_refd = self.expr.refd(True, ref_state)
        if self in ref_state.expr_vars:
            var = ref_state.expr_vars[self]
        else:
            var = ref_state.fresh_var()
            ref_state.defs.append(VDef(var, Aggregate(expr_refd, self.op)))
            ref_state.expr_vars[self] = var
        return Ref(var)


class Const(Expr):
    def __init__(self, value) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Const({self.value})"

    def refd(self, force: bool, ref_state: RefState) -> "Expr":
        if force:
            if self in ref_state.expr_vars:
                var = ref_state.expr_vars[self]
            else:
                var = ref_state.fresh_var()
                ref_state.defs.append(VDef(var, self))
                ref_state.expr_vars[self] = var
            return Ref(var)
        else:
            return self


class Mul(Expr):
    left: Expr
    right: Expr

    def __init__(self, left: Expr, right: Expr) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"Mul({self.left}, {self.right})"

    def refd(self, force: bool, ref_state: RefState) -> "Expr":
        left_refd = self.left.refd(False, ref_state)
        right_refd = self.right.refd(False, ref_state)
        if force:
            if self in ref_state.expr_vars:
                var = ref_state.expr_vars[self]
            else:
                var = ref_state.fresh_var()
                ref_state.defs.append(CDef(var, Mul(left_refd, right_refd)))
                ref_state.expr_vars[self] = var
            return Ref(var)
        else:
            return Mul(left_refd, right_refd)


class Ref(Expr):
    def __init__(self, var) -> None:
        self.var = var

    def __repr__(self) -> str:
        return f"Ref({self.var})"

    def refd(self, force: bool, ref_state: RefState) -> "Expr":
        return self


class Graphable:
    def refd(self, ref_state: RefState) -> "Graphable":
        raise RuntimeError("Abstract")


class DefGraphable(Graphable):
    var: str

    def __init__(self, var: str) -> None:
        self.var = var

    def refd(self, ref_state: RefState) -> "Graphable":
        return self


class Def(DefGraphable):
    rrd: Rrd

    def __init__(self, var, rrd: Rrd) -> None:
        super().__init__(var)
        self.rrd = rrd

    def __repr__(self) -> str:
        return f"Def({self.var}, {self.rrd})"


class CDef(DefGraphable):
    expr: Expr

    def __init__(self, var, expr: Expr) -> None:
        super().__init__(var)
        self.expr = expr

    def __repr__(self) -> str:
        return f"CDef({self.var}, {self.expr})"


class VDef(DefGraphable):
    aggregate: Aggregate

    def __init__(self, var, aggregate: Aggregate) -> None:
        super().__init__(var)
        self.aggregate = aggregate

    def __repr__(self) -> str:
        return f"VDef({self.var}, {self.aggregate})"


class Comment(Graphable):
    def __init__(self, text) -> None:
        self.text = text

    def __repr__(self) -> str:
        return f"Comment({self.text})"

    def refd(self, ref_state: RefState) -> "Graphable":
        return self


class GPrint(Graphable):
    expr: Expr

    def __init__(self, expr: Expr, format) -> None:
        self.expr = expr
        self.format = format

    def __repr__(self) -> str:
        return f"GPrint({self.expr}, {self.format})"

    def refd(self, ref_state: RefState) -> "Graphable":
        expr_refd = self.expr.refd(True, ref_state)
        return GPrint(expr_refd, self.format)


class Area(Graphable):
    expr: Expr

    def __init__(self, expr: Expr, color, legend) -> None:
        self.expr = expr
        self.color = color
        self.legend = legend

    def __repr__(self) -> str:
        return f"Area({self.expr}, {self.color}, {self.legend})"

    def refd(self, ref_state: RefState) -> "Graphable":
        expr_refd = self.expr.refd(True, ref_state)
        return Area(expr_refd, self.color, self.legend)


def outline(graphables: List[Graphable]) -> List[Graphable]:
    ref_state = RefState()
    ref_graphables = []
    for graphable in graphables:
        graphable_refd = graphable.refd(ref_state)
        ref_graphables.append(graphable_refd)
    return ref_state.defs + ref_graphables


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