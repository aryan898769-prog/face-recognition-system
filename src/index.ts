import { greet } from "./greeter";

const name = process.argv[2] ?? "World";
console.log(greet(name));
