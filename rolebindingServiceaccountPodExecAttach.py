import subprocess
import json
import re


def replace_annotations_and_print_matched(json_text):
    # 使用正则表达式匹配 "annotations" 字段及其值
    pattern = r'"annotations": {.*?\n\s*},'
    matches = re.findall(pattern, json_text, flags=re.DOTALL)
    replace = '"annotation":"0",'
    # 替换匹配内容为空字符串
    get_annotations = re.sub(pattern, replace, json_text, flags=re.DOTALL)
    # 使用 JSON 库解析整个 JSON 字符串
    return get_annotations


def validate_cluster_role_binding(json_text):
    # 解析 RoleBinding json
    try:
        json_text = replace_annotations_and_print_matched(json_text)
        crb_data = json.loads(json_text)
        name = crb_data["metadata"]["name"]
        if name == "gce:podsecuritypolicy:calico-sa" or name.startswith("system:"):
            return f"\033[1;34;40m{name}：系统相关的serviceaccount，不进行检查\033[0m"
        elif crb_data["roleRef"]:
            service_account_names = [subject['name'] for subject in crb_data.get('subjects', []) if
                                     subject.get('kind') == 'ServiceAccount']
            if (not service_account_names):
                return f"\033[1;34;40m{name}：没有serviceaccount，不进行检查\033[0m"
            role_ref = crb_data["roleRef"]
            if (
                    role_ref["apiGroup"] == "rbac.authorization.k8s.io"
                    and role_ref["kind"] == "Role"
            ):
                role_name = role_ref["name"]
                get_namespace_command = f"kubectl get role --all-namespaces |grep {role_name}"
                role_info = subprocess.run(get_namespace_command, shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE).stdout.decode('utf-8')
                role_namespace = role_info.split()[0]
                get_json_command = f"kubectl get role {role_name} -n {role_namespace} -o json"
                result = subprocess.run(get_json_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                get_result = result.stdout.decode('utf-8')
                cr_json_data = replace_annotations_and_print_matched(get_result)
                cr_data = json.loads(cr_json_data)
                rules = cr_data["rules"]
                for rule in rules:
                    if ("apiGroups" not in rule):
                        continue
                    if (any(api_group in ["", "*"] for api_group in rule.get("apiGroups", [])) and
                            any(resource in ["*", "pods/exec", "pods/attach"] for resource in
                                rule.get("resources", [])) and
                            any(verb in ["*", "get", "create"] for verb in rule.get("verbs", []))):
                        return f"\033[1;31;40m{service_account_names[0]}：允许 Pods/exec 或 pods/attach\033[0m"
                return f"{service_account_names[0]}：不允许 Pods/exec 或 pods/attach"

    except Exception as e:
        return f"解析 JSON 时出错：{str(e)}"


# 执行 kubectl 命令来获取 RoleBinding 列表
command = "kubectl get rolebindings --all-namespaces"
result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 如果命令成功执行，处理其输出
if result.returncode == 0:
    output = result.stdout.decode('utf-8').split('\n')[1:]

    # 提取 namespace 和 name 存储到变量
    namespaces = []
    names = []

    for line in output:
        if line:
            columns = line.split()
            namespace = columns[0]
            name = columns[1]
            namespaces.append(namespace)
            names.append(name)

    # 遍历一组namespace、name名称
    for namespace, name in zip(namespaces, names):
        # 执行 kubectl 命令来获取特定 Role 的 json
        get_command = f"kubectl get rolebinding {name} -n {namespace} -o json"
        get_result = subprocess.run(get_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 如果命令成功执行，打印 json 输出
        if get_result.returncode == 0:
            json_output = get_result.stdout.decode('utf-8')
            test_result = validate_cluster_role_binding(json_output)
            print(test_result)
        else:
            print("获取json不成功")
else:
    print("获取rolebinding name不成功")
