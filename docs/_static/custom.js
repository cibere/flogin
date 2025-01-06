document.addEventListener('DOMContentLoaded', () => {
    // Move the attribute tables to be between the signature and content
    const tables = document.querySelectorAll('.py-attribute-table[data-move-to-id]');
    tables.forEach(table => {
        let element = document.getElementById(table.getAttribute('data-move-to-id'));
        let parent = element.parentNode;
        // insert ourselves after the element
        parent.insertBefore(table, element.nextSibling);
    });

    // Use attribute table to find all decorators and add a @ to the front of their signature
    const decoBadges = document.querySelectorAll("li.py-attribute-table-entry>span.py-attribute-table-badge[title='decorator'][data-name]");
    decoBadges.forEach(decoBadge => {
        let name = decoBadge.getAttribute("data-name");
        let el = document.getElementById(name);
        let span = el.querySelector("span.sig-name>span.pre");

        span.innerHTML = `@${span.innerHTML}`;
        console.log(`Decorator: ${name}`);
        
        // This removes the parens from any deco with a single param. Will probably need to eventually update
        let params = el.getElementsByClassName("sig-param");
        if (params.length === 1){
            params[0].remove();
            let parens = el.getElementsByClassName("sig-paren");
            for (let _ in parens) {
                parens[0].remove();
            }
        }
    })
});