import os
import sys

apache_vhosts_path = '/etc/httpd/conf/extra/httpd-vhosts.conf'

def host_exists(vhosts_content, host_name):
    return f'ServerName {host_name}' in vhosts_content

def check_host(host_name):
    with open(apache_vhosts_path, 'r') as apache_vhosts_file:
        vhosts_content = apache_vhosts_file.read()
        return host_exists(vhosts_content, host_name)

def create_host(host_name):
    host_path = f'/srv/http/{host_name}'

    if check_host(host_name):
        print(f'Host <{host_name}> already exists')
        sys.exit(1)

    os.makedirs(host_path, exist_ok=True)

    with open(os.path.join(host_path, 'index.html'), 'w') as index_file:
        index_file.write(f'<html><body><h1>{host_name} is working!</h1></body></html>')

    os.system(f'chmod -R 755 {host_path}')

    apache_config = f"""
    <VirtualHost *:80>
        ServerAdmin admin@localhost
        DocumentRoot {host_path}
        ServerName {host_name}
        
        <Directory "/srv/http/olaf.local">
            AllowOverride All
            Require all granted
        </Directory>
        
        ErrorLog /var/log/httpd/{host_name}-error.log
        CustomLog /var/log/httpd/{host_name}-access.log combined
    </VirtualHost>
    """

    with open(apache_vhosts_path, 'a') as apache_vhosts_file:
        apache_vhosts_file.write(apache_config)

    with open('/etc/hosts', 'a') as hosts_file:
        hosts_file.write(f'127.0.0.1 {host_name}\n')

    os.system('sudo systemctl restart httpd')

    print(f'Host <{host_name}> was created')

def remove_host(host_name):
    if not check_host(host_name):
        print(f'Host <{host_name}> not found')
        sys.exit(1)

    with open(apache_vhosts_path, 'r') as apache_vhosts_file:
        lines = apache_vhosts_file.readlines()

    with open(apache_vhosts_path, 'r') as apache_vhosts_file:
        vhosts_content = apache_vhosts_file.read()

    vhosts_blocks = vhosts_content.split('</VirtualHost>')
    updated_vhosts_blocks = [block for block in vhosts_blocks if f'ServerName {host_name}' not in block]
    updated_vhosts_content = '</VirtualHost>'.join(updated_vhosts_blocks)
    with open(apache_vhosts_path, 'w') as apache_vhosts_file:
        apache_vhosts_file.write(updated_vhosts_content)

    with open('/etc/hosts', 'r') as hosts_file:
        lines = hosts_file.readlines()

    with open('/etc/hosts', 'w') as hosts_file:
        for line in lines:
            if not f'127.0.0.1 {host_name}' in line:
                hosts_file.write(line)


    os.system('systemctl restart httpd')

    print(f'Host <{host_name}> was removed')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Use: sudo python3 create.py <create|remove> <hostname>")
        sys.exit(1)

    operation = sys.argv[1].lower()
    host_name = sys.argv[2]

    if operation == 'create':
        create_host(host_name)
    elif operation == 'remove':
        remove_host(host_name)
    else:
        print("Invalid operation")
        sys.exit(1)