import re

def extract_app_js_from_index(index_content):
    result = re.search('"([/\\d\\w]*)((?:app|index|main)[.\\d\\w]{0,50}.js)"', index_content)
    if result:
        return result.group(1,2)
    else:
        return (False, False)
    
def extract_runtime_js_from_index(index_content):
    result = re.search('"([/\\d\\w]*)((?:runtime)[.\\d\\w]{0,50}.js)"', index_content)
    if result:
        return result.group(1,2)
    else:
        return (False, False)
    
def extract_js_from_app(content):
    matches = re.findall("\"(chunk-[\\d\\w]{5,10})\":\"([\\d\\w]{5,10})\"", content)
    results = []
    for result in matches:
        results.append("js/"+result[0]+"."+result[1]+".js")
        results.append("js/"+result[0]+"."+result[1]+".js.map")
    return results


def extract_js_from_index_vue_like(index_content):
    matches = re.findall("js\\/chunk-[\\w\\d]{5,10}\\.[\\w\\d]{5,10}\\.js", index_content)
    results = []
    for result in matches:
        results.append(result+".map")
        results.append(result)
    return results

def extract_js_from_index_react_like_chunk(prefix, index_content):
    results = []
    match = re.search('({(?:\\d\\w{1,10}:"[\\d\\w]{5,10}",*)+}).{1,30}.chunk.js', index_content)
    if match:
        match = match.group(0)
        submatches = re.findall('(\\d{1,3}):"([\\d\\w]{5,10})"', match)
        for submatch in submatches:
            results.append(prefix+submatch[0]+"."+submatch[1]+"."+"chunk.js")
            results.append(prefix+submatch[0]+"."+submatch[1]+"."+"chunk.js.map")
    
    return results

def extract_js_from_runtime_no_chunk(prefix, index_content):  #TODO
    results = []
    match = re.search('({(?:\\d\\w{1,10}:"[\\d\\w]{5,10}",*)+}).{1,30}.chunk.js', index_content)
    if match:
        match = match.group(0)
        submatches = re.findall('(\\d{1,3}):"([\\d\\w]{5,10})"', match)
        for submatch in submatches:
            results.append(prefix+submatch[0]+"."+submatch[1]+"."+"chunk.js")
            results.append(prefix+submatch[0]+"."+submatch[1]+"."+"chunk.js.map")
    
    return results

def extract_js_from_index_index_like(prefix, app_js_content):
    results = []
    matches = re.findall(prefix.lstrip('/').replace('/','\\/')+ '([\\d\\w.]+.js)', app_js_content)
    for match in matches:
        results.append(prefix + match+".map")
        results.append(prefix + match)
    return results

def extract_js_from_runtime(prefix, runtime_js_content):
    results = []
    common_js_number = re.search('(\\d{1,5})===.*', runtime_js_content)
    if(common_js_number):
        common_js_number = common_js_number.group(1)
    else:
        common_js_number=-1
    match = re.search('({(?:[\\d\\w]{1,10}:"[\\d\\w]{5,20}",*)+}).{1,30}\\.js', runtime_js_content)
    if match:
        match = match.group(0)
        submatches = re.findall('([\\d\\w]{1,10}):"([\\d\\w]{5,20})"', match)
        for submatch in submatches:
            if int(submatch[0])==common_js_number:
                results.append(prefix+"common."+submatch[1]+".js")
                results.append(prefix+"common."+submatch[1]+".js.map")
                continue
            results.append(prefix+submatch[0]+"."+submatch[1]+".js")
            results.append(prefix+submatch[0]+"."+submatch[1]+".js.map")
    
    return results

