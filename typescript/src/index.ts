import { escapeHTML } from "./test";

const world = 'world';

function hello(who: string = world): string {
  return escapeHTML(`<b>Hello ${who}!</b>`);
}

document.write(hello());
alert(hello());
