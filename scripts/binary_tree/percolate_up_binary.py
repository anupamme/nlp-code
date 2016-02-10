import json
import sys

def find_keywords_subtree(node):
    if node['left'] == {} and node['right'] == {}:
            return
    merge = node['keywords']
    if node['left'] != {}:
        find_keywords_subtree(node['left'])
        for word in node['left']['keywords']:
            if word in merge:
                merge[word] = merge[word] + node['left']['keywords'][word]
            else:
                merge[word] = node['left']['keywords'][word]
    if node['right'] != {}:
        find_keywords_subtree(node['right'])
        for word in node['right']['keywords']:
            if word in merge:
                merge[word] = merge[word] + node['right']['keywords'][word]
            else:
                merge[word] = node['right']['keywords'][word]
    
    node['keywords'] = merge
    return
    


if __name__ == "__main__":
    data = json.loads(open(sys.argv[1], 'r').read())
    find_keywords_subtree(data['root'])
    f = open(sys.argv[2], 'w')
    f.write(json.dumps(data))
    f.close()