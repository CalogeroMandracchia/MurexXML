import textwrap
import argparse
from pathlib import Path
import sys
import os

global_args = None

def create_dir(dirname):
    try:
        if not Path(dirname).is_dir():
            os.mkdir(dirname)
        return dirname
    except OSError:
        sys.exit(f"Creation of the directory {dirname} failed")

def write_file(filename, data):
    with open(filename, 'w+') as f:
        f.write(data)
    f.closed

def read_file(filename):
    with open(filename) as f:
        read_data = f.read()
    f.closed
    return read_data

def read_lines(filename):
    data = list()        
    with open (filename, "r") as fh:
        for line in fh:
            data.append(line.strip())
    return data

def get_template_proc(name):
    global global_args
    options = {'group': 'MX', 'user': 'MUREXBO', 'desk': '', 'predefined': 'Yes'}
    for opt in options:
        if 'opt' in global_args:
            options[opt] = global_args[opt]

    template_proc = textwrap.dedent(f"""\
    <?xml version="1.0"?>
    <!DOCTYPE Script>
    <Script>
        <LoginContext>
            <Group>{options['group']}</Group>
            <User>{options['user']}</User>
            <Desk>{options['desk']}</Desk>
        </LoginContext>
        <Name>{name}</Name>
        <Predefined>{options['predefined']}</Predefined>
    </Script>""")
    return template_proc

def get_template_req(name):
    global global_args
    options = {'platformname': 'MX', 'nickname': 'MXPROCESSINGSCRIPT', 'family': 'Generic'}
    for opt in options:
        if 'opt' in global_args:
            options[opt] = global_args[opt]

    template_req = textwrap.dedent(f"""\
    <?xml version="1.0"?>
    <!DOCTYPE XmlRequestScript>
    <XmlRequestScript>
        <ServicePlatformName>{options['platformname']}</ServicePlatformName>
        <ServiceNickName>{options['nickname']}</ServiceNickName>
        <Family>{options['family']}</Family>
        <Query>applyXmlAction</Query>
        <Header>xml/{name}_proc.xml</Header>
        <Answer>xml/{name}_out.xml</Answer>
        <Log>xml/{name}_log.xml</Log>
    </XmlRequestScript>""")
    return template_req

def create_xml(file_name, data):
    global global_args
    if 'output' in global_args:
        file_name = f"{global_args['output']}/{file_name}"
    write_file(file_name, data)

def create_req(name):
    data_req = get_template_req(name)
    create_xml(f'{name}_req.xml', data_req)

def create_proc(name):
    data_proc = get_template_proc(name)
    create_xml(f'{name}_proc.xml', data_proc)

def create_all(name):
    print(f'processing ->{name}<-')
    create_req(name)
    create_proc(name)

def argument_parse():
    ap = argparse.ArgumentParser(description='Tool for creating request and proc files for Murex')
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--name", help="set the name of the datamart to be created")
    group.add_argument("-i", "--input",
        help="pass a file_name and use it as the input", 
        type=lambda path_file: ap.error(f'the file "{path_file}" does not exist') if not Path(path_file).is_file() else path_file )
    ap.add_argument("-o", "--output", 
        help="pass a file_name and use it as the output directory",
        type= lambda dirname: create_dir(dirname) )
    ap.add_argument("--group",  help="define a Group for proc files, like 'MX'")
    ap.add_argument("--user",  help="define a User for proc files, like 'MUREXBO'")
    ap.add_argument("--desk",  help="define a Desk for proc files")
    ap.add_argument("--predefined",  help="define if it is predefined, default 'Yes'")
    ap.add_argument("--platformname",  help="define a PlatformName for proc files, like 'MX'")
    ap.add_argument("--nickname",  help="define a NickName for proc files, like 'MXPROCESSINGSCRIPT'")
    ap.add_argument("--family",  help="define a family for proc files, like 'Generic'")
    args = vars(ap.parse_args())
    global global_args
    global_args = args
    return args

def main():
    args = argument_parse()
    name = args['name'] # DATAMART_PURGE_JOBS
    if args['input']:
        lines = read_lines(args['input'])
        for line in lines:
                create_all(line)
    else:
        create_all(name)

if __name__== "__main__":  
    main()