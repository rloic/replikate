if path.startswith("url="):
    print('>> Loading remote configuration')
    repo = path[5:path.index(']')]
    if repo[-1] == '/':
        repo = repo[:-1]
    path = path[path.index(']') + 1:]
    if os.path.exists(path):
        print('  The file {} already exist, would you erase it ? [y/N]:'.format(path), end='')
        text = input()
        while text not in ["", "y", "Y", "n", "N"]:
            text = input()
        if text in ['y', 'Y']:
            print('  Erasing local file')
            os.remove(path)
            urllib.request.urlretrieve(repo + '/' + path, path)
        else:
            print('  Loading aborted, the script will use the local file')
    else:
        urllib.request.urlretrieve(repo + '/' + path, path)
    print('<< Loading remote configuration')
