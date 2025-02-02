document.addEventListener('DOMContentLoaded', () => {
    // Move the attribute tables to be between the signature and content
    const tables = document.querySelectorAll('.py-attribute-table[data-move-to-id]');
    tables.forEach(table => {
        let element = document.getElementById(table.getAttribute('data-move-to-id'));
        let parent = element.parentNode;
        // insert ourselves after the element
        parent.insertBefore(table, element.nextSibling);
    });
});