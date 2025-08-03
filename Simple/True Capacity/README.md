# True Value

---

This python script determines the _real_ capacity of some device you have or some device you're looking to purchase

### What the hell are you talking about?

---

Alright so you bought a 5 TB external hard drive, you plug it in and open the properties on the new drive. Lo and behold, 4.55 TBs. What gives? something something binary multiplicatives don't cleanly equate to decimal multiplicatives.

#### Alright really _now_ what are you talking about?

---

This is all about how numbers work on a technical level. Decimal (the numbers we use all the time) makes for very clean expressions of magnitude; 10 is literally ten 1s, 1000 is literally a thousand 1s. Manufacturers use this same decimal math when selling hardware. "Here's your thousand bytes of RAM, fresh off the press. One kilobyte if you will." they say.

Unfortunately computers don't use decimal math. In binary, numbers are built on powers of 2 which tends to not round very cleanly. For example, a computer references a thousand bytes in memory, or 2^10, as 1024 bytes. This means that your 1000 bytes of RAM out of the box really equates to _less than_ one kilobyte in memory. While the difference here is fairly nominal. When you start getting into the Gigas and Teras it can become quite meaningful.

Here's a chart for reference that details the differences in decimal and binary

| Decimal Value | SI Prefix | Name   | Binary Value | IEC Prefix | Name  | JEDEC Prefix | Name |
| ------------- | --------- | ------ | ------------ | ---------- | ----- | ------------ | ---- |
| 10³           | k         | kilo   | 2¹⁰          | Ki         | kibi  | K            | kilo |
| 10⁶           | M         | mega   | 2²⁰          | Mi         | mebi  | M            | mega |
| 10⁹           | G         | giga   | 2³⁰          | Gi         | gibi  | G            | giga |
| 10¹²          | T         | tera   | 2⁴⁰          | Ti         | tebi  | T            | tera |
| 10¹⁵          | P         | peta   | 2⁵⁰          | Pi         | pebi  | —            | —    |
| 10¹⁸          | E         | exa    | 2⁶⁰          | Ei         | exbi  | —            | —    |
| 10²¹          | Z         | zetta  | 2⁷⁰          | Zi         | zebi  | —            | —    |
| 10²⁴          | Y         | yotta  | 2⁸⁰          | Yi         | yobi  | —            | —    |
| 10²⁷          | R         | ronna  | 2⁹⁰          | Ri         | robi  | —            | —    |
| 10³⁰          | Q         | quetta | 2¹⁰⁰         | Qi         | quebi | —            | —    |
