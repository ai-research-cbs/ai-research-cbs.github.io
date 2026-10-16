# How this site fits together

Jekyll turns Markdown pages and two data files into ordinary HTML. There is no server application.

Think of `sections.yml` as the directory sign and `readings.yml` as the reading shelf.
Each page selects its shelf by `section` and `page`. Economic Implications also selects four groups.
Years stay numeric, so Jekyll 3.10 can sort each list reliably.

The shared layout supplies the course-style header, subsection links, outline, and footer.
The reading include retains the course's document icons and citation format.
Source Serif 4 headings, Helvetica body text, and the clay accent follow this site's build spec.

JavaScript only opens the phone menu and fills the desktop outline.
Pages, readings, and navigation remain usable when JavaScript is off.
On phones, the exposure table shows each row vertically. Column names remain visible beside each value.

Jekyll 3.10 predates Ruby 4. The Gemfile explicitly includes libraries that modern Ruby no longer bundles.
The built site needs none of those libraries in the browser.

Run the structure check after building. The browser check catches clipped navigation and phone overflow.
Keep test evidence outside the published site. External links can block automated requests; inspect those responses separately.
