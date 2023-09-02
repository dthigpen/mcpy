from mcpy.cmd.nbt import *


def test_nbt():
    assert str(Bool(True)) == 'true'
    assert str(Bool(False)) == 'false'
    assert str(Short(1)) == '1s'
    assert str(Float(123.4)) == '123.4f'
    assert str(Byte(123)) == '123b'
    assert str(Str('Hello!')) == '"Hello!"'
    assert str(Str('Hello "Human"!')) == '"Hello \\"Human\\"!"'
    assert str(NbtObj({'foo':Byte(123),'123':'aaa'})) == '{"foo": 123b, "123": "aaa"}'

    nbt = NbtPath('this')
    assert str(nbt) == 'this'
    assert str(nbt.key('ingredient')) == 'this.ingredient'
    assert str(nbt.key('ingredient').where(123)) == 'this.ingredient[123]'
    obj = NbtObj({'foo':'bar','123':'aaa'})
    assert str(obj) == '{"foo": "bar", "123": "aaa"}'
