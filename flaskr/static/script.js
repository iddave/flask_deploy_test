var id = null;
var orig_question = null;
var orig_answer = null;
var orig_link = null;
document.querySelectorAll('.edit-button').forEach(function (button) {
    button.addEventListener('click', function () {

        orig_question = this.getAttribute('data-question');
        orig_answer = this.getAttribute('data-answer');
        orig_link = this.getAttribute('data-link');
        id = this.getAttribute('data-id');

        console.log(`EDIT btn click, orig_question: ${orig_question}`)
        console.log(`EDIT btn click, id: ${id}`)
        document.getElementById('question_field_edit').value = orig_question;
        document.getElementById('answer_field_edit').value = orig_answer;
        document.getElementById('answer_link_field_edit').value = orig_link;

        // Show the modal
        document.getElementById('overlay').style.display = 'block';
        // document.getElementById('overlay').style.display = 'block';
        // document.getElementById('edit_form').style.display = 'block';
    });
});

document.getElementById('save-edit_button').addEventListener('click', function () {
    var question = document.getElementById('question_field_edit').value;
    var answer = document.getElementById('answer_field_edit').value;
    var link = document.getElementById('answer_link_field_edit').value;

    console.log(`SAVE btn click, id: ${id}`)

    fetch('/test/update_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id,
            orig_question: orig_question,
            orig_answer: orig_answer,
            orig_link: orig_link,
            question: question,
            answer: answer,
            link: link
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // Optionally, update the UI to reflect the changes
            // Close the modal, etc.
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    id = null;
    closeForm();
});

document.querySelector('.btn-close').addEventListener('click', closeForm);

document.getElementById('overlay').addEventListener('click', function (event) {
    if (event.target === this) {
        document.getElementById('overlay').style.display = 'none';
    }
});

function closeForm(){
    document.getElementById('overlay').style.display = 'none';
}

function confirmDelete() {
    var result = confirm("Удалить эту запись?");
    if (result) {
        // User clicked "OK", proceed with deletion
        fetch(`/test/delete_record`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: id,
                orig_question: orig_question,
                orig_answer: orig_answer,
                orig_link: orig_link
            })
        })
        .then(response => response.json())
        .then(data => {
            // Handle the response from the server
            console.log(data);
        })
        .catch(error => console.error('Error:', error));
        closeForm();
    } else {
        // User clicked "Cancel", do nothing
    }
}



