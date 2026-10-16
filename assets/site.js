// Keep the course menu and page outline; all content is available without JavaScript.
document.documentElement.classList.add('has-js');
const button = document.querySelector('.menu-toggle');
const menu = document.querySelector('#topnav');
function closeMenu() {
  menu.classList.remove('is-open');
  button.setAttribute('aria-expanded', 'false');
}
button.addEventListener('click', () => {
  const open = menu.classList.toggle('is-open');
  button.setAttribute('aria-expanded', String(open));
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menu.classList.contains('is-open')) {
    closeMenu();
    button.focus();
  }
});
document.addEventListener('click', (event) => {
  if (!event.target.closest('.topbar')) closeMenu();
});
matchMedia('(min-width:820px)').addEventListener('change', closeMenu);

const outline = document.querySelector('#outline');
document.querySelectorAll('article h2, article h3').forEach((heading, index) => {
  if (!heading.id) heading.id = `section-${index + 1}`;
  const item = document.createElement('li');
  if (heading.tagName === 'H3') item.className = 'outline-sub';
  const link = document.createElement('a');
  link.href = `#${heading.id}`;
  link.textContent = heading.textContent;
  item.append(link);
  outline.append(item);
});
document.querySelector('.page-outline').hidden = !outline.children.length;
