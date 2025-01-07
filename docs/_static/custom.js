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
    const decoBadges = document.querySelectorAll("li.py-attribute-table-entry>span.py-attribute-table-badge[title='decorator']");
    console.log(decoBadges);
    decoBadges.forEach(decoBadge => {
        let name = decoBadge.dataset["name"];
        let el = document.getElementById(name);
        let span = el.querySelector("span.sig-name>span.pre");

        span.innerHTML = `@${span.innerHTML}`;
        console.log(`Decorator: ${name}`);

        let isFac = decoBadge.dataset['isfactory']

        console.log(`isFac`, isFac)
        
        if (isFac === "False"){
            let params = el.getElementsByClassName("sig-param");
            params[0].remove();
            console.log(`Remove`, params[0]);
            let parens = el.getElementsByClassName("sig-paren");
            while (parens.length > 0) {
                parens[0].remove();
            }
        }
    })
});