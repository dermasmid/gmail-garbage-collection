import google_workspace


def connect():
    global mailbox
    mailbox = google_workspace.gmail.GmailClient()


def get_emails_data():
    print("Getting messages....")
    messages_data = {}

    msgs = mailbox.get_messages("inbox", batch=True, message_format="full")
    index = 1
    for msg in msgs:
        print(f"Got so far {index} messages...", end="\r")
        index += 1

        if not msg.from_ in messages_data:
            messages_data[msg.from_] = {"size": 0, "msgs": []}

        messages_data[msg.from_]["msgs"].append(msg.gmail_id)

        for attachment in msg.attachments:
            if attachment.payload:  # TypeError: object of type 'NoneType' has no len()
                messages_data[msg.from_]["size"] += len(attachment.payload)

    return messages_data


def sort_messages_by_size(messages_data):
    return sorted(
        messages_data,
        key=lambda email_address: messages_data[email_address]["size"],
        reverse=True,
    )


def sort_messages_by_quantity(messages_data):
    return sorted(
        messages_data,
        key=lambda email_address: len(messages_data[email_address]["msgs"]),
        reverse=True,
    )


def delete_from_sender(messages_data, email_address):
    msgs = messages_data[email_address]["msgs"]

    for msg_id in msgs:
        mailbox.delete_message(msg_id)


def trash_from_sender(messages_data, email_address):
    msgs = messages_data[email_address]["msgs"]

    for msg_id in msgs:
        mailbox.trash_message(msg_id)


if __name__ == "__main__":
    connect()
    print(f"Running on {mailbox.email_address}")
    messages_data = get_emails_data()
    print("\nGot your messages!")

    while True:
        sort_by = input(
            "List your messages by:\n1: quantity\n2: size\nSelect (1/2)\nLeave empty to quit: "
        )
        if not sort_by:
            break
        if sort_by == "1":
            email_addresses = sort_messages_by_quantity(messages_data)
        elif sort_by == "2":
            email_addresses = sort_messages_by_size(messages_data)

        number_to_display = int(
            input(
                "Imma list the top email addresses, How many do you want me to list?: "
            )
        )
        email_addresses = email_addresses[:number_to_display]

        while True:
            for index, email_address in enumerate(email_addresses):
                print(
                    f'{index}:{email_address}: messages: {len(messages_data[email_address]["msgs"])}; total attachments size: {str(messages_data[email_address]["size"] / (1024 * 1024))[:5]}Mb'
                )
            selected_emails = input(
                'Enter the numbers of email addresses you want to perform actions separated by ",", or leave empty if you are done with this selection: '
            )
            if not selected_emails:
                break
            action = input(
                "What do you want to do with all the emails from those senders?\n1: Delete\n2: Move to trash\nLeave empty to select diffrent email: "
            )
            if not action:
                continue

            selected_emails = selected_emails.split(",")
            for selected_email in selected_emails:
                selected_email = email_addresses[int(selected_email)]

                if action == "1":
                    print(f"Deleting all emails from {selected_email}")
                    delete_from_sender(messages_data, selected_email)
                elif action == "2":
                    print(f"Trashing all emails from {selected_email}")
                    trash_from_sender(messages_data, selected_email)
                email_addresses.remove(selected_email)
