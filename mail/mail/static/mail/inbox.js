document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';


  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // When the send button is clicked, send the email
  document.querySelector('#compose-send').addEventListener('click', () => {

    // Construct a message object
    const message = {
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value,
    };

    // Send the message!
    console.log('Sending message', message);
    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
          recipients: message.recipients,
          subject: message.subject,
          body: message.body,
        })
      })
      .then(response => response.json())
      .then(result => {
        // Print result
        console.log(result);
      });

    // Switch back to the inbox
    load_mailbox('inbox');
  });


}


function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch the emails
  fetch('/emails/' + mailbox)
    .then(response => response.json())
    .then(emails => {
      // Print emails
      console.log(emails);

      // loop through emails and display them as divs in the emails-view div
      for (let i = 0; i < emails.length; i++) {
        const email = emails[i];
        let read = emails[i].read ? 'read' : 'unread';
        const email_div = document.createElement('div');
        email_div.classList.add('single-email');
        email_div.innerHTML = `
    <div class="${read}" data-identifier="${email.id}">
      <div class="email-sender">${email.sender}</div>
      <div class="email-subject">${email.subject}</div>
      <div class="email-body">${email.body}</div>
      <hr>
    </div>
  `;
        // add event listener to each email div
        email_div.addEventListener('click', () => {
          read_email(email);
        });
        document.querySelector('#emails-view').appendChild(email_div);
      }
    });
}

function read_email(email) {
  // set display to none for all views except email-view
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';
  // email’s sender, recipients, subject, timestamp, and body.
  // present the email in the email-view div
  document.querySelector('#email-view').innerHTML = `
    <div class="email-sender"><strong>Sender:</strong> ${email.sender}</div>
    <div class="email-recipients"><strong>Recipients:</strong> ${email.recipients}</div>
    <hr>
    <div class="email-timestamp"> <strong>Time: </strong>${email.timestamp}</div>
    <div class="email-subject"><strong>Subject:</strong> ${email.subject}</div>
    <div class="email-body-title"><strong>Body:</strong> </div>
    <div class="email-body">${email.body}</div>
    <hr>
    <button class="btn btn-primary" id="email-back">Back</button>
    <button class="btn btn-primary" id="email-reply">Reply</button>
  `;
  // if the email is archived present the unarchive button
  if (email.archived) {
    document.querySelector('#email-view').innerHTML += `
    <button class="btn btn-danger" id="email-archive">Unarchive</button>
    `;
  } else {
    document.querySelector('#email-view').innerHTML += `
    <button class="btn btn-danger" id="email-archive">Archive</button>
    `;
  }
  // add event listeners to the repy button 
  document.querySelector('#email-reply').addEventListener('click', () => {
    reply_email(email);
  });
  document.querySelector('#email-back').addEventListener('click', () => {
    load_mailbox('inbox');
  });
  document.querySelector('#email-archive').addEventListener('click', () => {
    fetch('/emails/' + email.id, {
      method: 'PUT',
      body: JSON.stringify({
        archived: !email.archived
      })
    })
    load_mailbox('inbox');
  });


  // update the email to read
  fetch('/emails/' + email.id, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })


}

function reply_email(email) {
  // set display to none for all views except compose-view

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';


  // reply to the email
  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `
On ${email.timestamp} ${email.sender} wrote:
  ${email.body}
  `;

  // When the send button is clicked, send the email
  document.querySelector('#compose-send').addEventListener('click', () => {

    // Construct a message object
    const message = {
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value,
    };

    // Send the message!
    console.log('Sending message', message);
    fetch("/emails", {
        method: "POST",
        body: JSON.stringify({
          recipients: message.recipients,
          subject: message.subject,
          body: message.body,
        }),
      })
      // Take the return data and parse it in JSON format.
      .then((response) => response.json())
      .then((result) => {
        load_mailbox("sent", result);
      })
      .catch((error) => console.log(error));
    load_mailbox('sent');
  });

}