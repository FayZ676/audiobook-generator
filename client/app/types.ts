import { z } from "zod";

export const AgeEnum = z.enum(["young", "middle-aged", "old"]);
export const GenderEnum = z.enum(["male", "female"]);
