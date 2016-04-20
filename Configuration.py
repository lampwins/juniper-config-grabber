import paramiko


class Configuration(object):

    client = paramiko.SSHClient()

    def __init__(self, host, username, password, root_sections):

        print "Retrieving config for %s...", host

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.client.connect(host, username=username, password=password)
        self.client.load_system_host_keys()

        self.root_sections_list = []

        for section in root_sections:
            stdin, stdout, stderr = self.client.exec_command(
                'show configuration ' + section + ' | display set | no-more')

            self.root_sections_list.append([section, stdout.readlines()])

        self.root_sections = dict(self.root_sections_list)

        self.client.close()

    def get_lines(self, section, match_terms, except_terms):

        return [x for x in section if all(m in x for m in match_terms) and not any(e in x for e in except_terms)]

    def get_filtered_lines(self, section, match_terms, except_terms):

        return self.get_lines(self.root_sections[section], match_terms, except_terms)
