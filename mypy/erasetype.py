import typing

from mypy.types import (
    Type, TypeVisitor, UnboundType, ErrorType, AnyType, Void, NoneTyp,
    Instance, TypeVar, Callable, TupleType, UnionType, Overloaded, ErasedType,
    TypeTranslator, BasicTypes, TypeList
)


def erase_type(typ: Type, basic: BasicTypes) -> Type:
    """Erase any type variables from a type.

    Also replace tuple types with the corresponding concrete types. Replace
    callable types with empty callable types.
    
    Examples:
      A -> A
      B[X] -> B[Any]
      Tuple[A, B] -> tuple
      Function[...] -> Function[[], None]
    """
    
    return typ.accept(EraseTypeVisitor(basic))


class EraseTypeVisitor(TypeVisitor[Type]):
    def __init__(self, basic: BasicTypes) -> None:
        self.basic = basic
    
    def visit_unbound_type(self, t: UnboundType) -> Type:
        assert False, 'Not supported'
    
    def visit_error_type(self, t: ErrorType) -> Type:
        return t
    
    def visit_type_list(self, t: TypeList) -> Type:
        assert False, 'Not supported'
    
    def visit_any(self, t: AnyType) -> Type:
        return t
    
    def visit_void(self, t: Void) -> Type:
        return t
    
    def visit_none_type(self, t: NoneTyp) -> Type:
        return t
    
    def visit_erased_type(self, t: ErasedType) -> Type:
        # Should not get here.
        raise RuntimeError()
    
    def visit_instance(self, t: Instance) -> Type:
        return Instance(t.type, [AnyType()] * len(t.args), t.line,
                        t.repr)
    
    def visit_type_var(self, t: TypeVar) -> Type:
        return AnyType()
    
    def visit_callable(self, t: Callable) -> Type:
        # We must preserve the type object flag for overload resolution to
        # work.
        return Callable([], [], [], Void(), t.is_type_obj())

    def visit_overloaded(self, t: Overloaded) -> Type:
        return t.items()[0].accept(self)
    
    def visit_tuple_type(self, t: TupleType) -> Type:
        return self.basic.tuple

    def visit_union_type(self, t: UnionType) -> Type:
        return AnyType()        # XXX: return underlying type if only one?

def erase_generic_types(t: Type) -> Type:
    """Remove generic type arguments and type variables from a type.

    Replace all types A[...] with simply A, and all type variables
    with 'Any'.
    """
    
    if t:
        return t.accept(GenericTypeEraser())
    else:
        return None


class GenericTypeEraser(TypeTranslator):
    """Implementation of type erasure"""
    
    # FIX: What about generic function types?
    
    def visit_type_var(self, t: TypeVar) -> Type:
        return AnyType()
    
    def visit_instance(self, t: Instance) -> Type:
        return Instance(t.type, [], t.line)


def erase_typevars(t: Type) -> Type:
    """Replace all type variables in a type with any."""    
    return t.accept(TypeVarEraser())


class TypeVarEraser(TypeTranslator):
    """Implementation of type erasure"""
    
    def visit_type_var(self, t: TypeVar) -> Type:
        return AnyType()
