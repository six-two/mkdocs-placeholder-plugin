# Tests: General

This page exists to check if variables behave the way I expect them to do.
So it may look very chaotic ;)

Variable | Value
---|---
TEST | `xTESTx`
LINK | [sLINKs](iLINKi)
CHECKBOX | xCHECKBOXx
Quoted string | xQUOTE_CHECKBOXxxTESTxxQUOTE_CHECKBOXx
DROPDOWN | xDROPDOWNx

## Replacement methods

Type | Test
---|---
Dynamic | dTESTd
Editable | eTESTe
HTML (allowed, should work) | iLINKi
HTML (prohibited, should fail) | iTESTi
Normal | xTESTx
Static | sTESTs

EDIT_TEST_END

<label><input data-input-for="QUOTE_CHECKBOX">Use double quotes</label>

<label>Label for dropdown<input data-input-for="DROPDOWN"></label>


## Intersecting variables

xTESTxxTESTxxTESTx

xTESTxTESTxTESTxTESTx

xxTESTxx

xTExTESTxSTx

## In different content

### Section title: xTESTx

- [xTESTx](#)
- _xTESTx_, *xTESTx*
- __xTESTx__
- `xTESTx`
- ++ctrl+xTESTx++
- <u>xTESTx</u>

```
xTESTx
```

!!! note "Admonition title: xTESTx"
    The contents are xTESTx

Direct link: <https://xTESTx>

Text can be {--deleted xTESTx--} and replacement text {++added xTESTx++}. This can also be
combined into {~~one xTESTx~>a single xTESTx~~} operation. {==Highlighting xTESTx==} is also
possible {>>and comments can be added inline xTESTx<<}.

{==

Some of this is taken from <https://squidfunk.github.io/mkdocs-material/reference/formatting/>

Test placeholder: xTESTx

==}

Dynamic keys: ++ctrl+xTESTx++, ++ctrl+"xTESTx"++

Static keys: ++ctrl+sTESTs++, ++ctrl+"sTESTs"++

Sub~xTESTx~script, super^xTESTx^script


## Invalid

xTEST TESTx XTESTX xTSTx x TEST x xTestx xTeSTx

## Combined variable

- <input data-input-for="COMB_FIRST_NAME">
- <input data-input-for="COMB_SURNAME">
- <input data-input-for="COMB_DOMAIN">
- Combined email address: xCOMB_EMAILx

## Bad practices

Bad name format: xBad_Name Formatx

This should cause a warning at build time: <input data-input-for="VARIABLE_DOES_NOT_EXIST">

## Test for Cross-Site Scripting

In input field | In normal page
---|---
<input data-input-for="XSS_ONE"> | xXSS_ONEx
<input data-input-for="XSS_TWO"> | xXSS_TWOx
<input data-input-for="XSS_THREE"> | xXSS_THREEx
console.log("xXSS_TWOx") | Check the browser console (F12)<script>setTimeout(function(){console.log("sXSS_TWOs")}, 1000); // This should output xXSS_TWOx, since scripts should not be modified</script>
