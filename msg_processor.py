

def get_header_field(msg):
    if msg.startswith("header: ") and msg.endswith(" [EOM]"):
        start_index = 8
        end_index = msg.find(" content: ")

        # "carve" out the field in the header field
        return msg[start_index: end_index]


def get_content_field(msg):
    if msg.endswith(" [EOM]"):
        start_index = msg.find(" content: ") + 10

        end_index = msg.find(" [EOM]")

        # "carve" out the field in the contents field
        return msg[start_index: end_index]