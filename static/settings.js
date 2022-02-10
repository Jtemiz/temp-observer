
/*
function addComToLocalStorage() {
    const entry = {
        comment: document.getElementById('addComToListBtn').value
    };
    let existingEntries = JSON.parse(localStorage.getItem('comBtn'));
    if (existingEntries == null) {
        existingEntries = [];
        localStorage.setItem('comBtn', JSON.stringify(entry));
    } else if (existingEntries.length >= 11) {
        this.alert.error('Maximale Anzahl an Kommentaren (10) erreicht. Bitte entfernen Sie ein bestehendes um ein neues hinzuzufügen.');
        return;
    } else {
        for (let i = 0; i < existingEntries.length; i++) {
            if (existingEntries[i].comment === document.getElementById('addComToListBtn').value) {
                return;
            }
        }
    }
    existingEntries.push(entry);
    localStorage.setItem('comBtn', JSON.stringify(existingEntries));
    this.comBtns = JSON.parse(localStorage.getItem('comBtn'));
    document.getElementById('addComToListBtn').value = '';
}
*/

function addComBtn() {
    com = document.getElementById('addComToListBtn').value;
    console.log(com)
    $.post( "/addCommentBtn", {
        comment: com
    });
    document.getElementById('addComToListBtn').value = '';
    window.location.href='/settings';
}

function deleteComBtn(e) {
    com = e.id
    console.log(com)
    $.post( "/deleteCommentBtn", {
        comment: com
    });
    window.location.href='/settings';
}