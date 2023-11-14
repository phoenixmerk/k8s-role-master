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
    # 解析 ClusterRoleBinding json
    try:
        json_text = replace_annotations_and_print_matched(json_text)
        crb_data = json.loads(json_text)
        name = crb_data["metadata"]["name"]
        if name in ["cluster-admin", "gce:podsecuritypolicy:calico-sa"] or name.startswith("system:"):
            return "00"
        elif crb_data["roleRef"]:
            role_ref = crb_data["roleRef"]
            if (
                    role_ref["apiGroup"] == "rbac.authorization.k8s.io"
                    and role_ref["kind"] == "ClusterRole"
            ):
                role_name = role_ref["name"]
                command = f"kubectl get clusterrole {role_name} -o json"
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
                        return "02"
                return "01"

    except Exception as e:
        return f"解析 JSON 时出错：{str(e)}"


# 执行 kubectl 命令来获取 ClusterRoleBinding 列表
command = "kubectl get clusterrolebinding  -o custom-columns=NAME:.metadata.name --no-headers"
result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 如果命令成功执行，处理其输出
if result.returncode == 0:
    output = result.stdout.decode('utf-8')
    output = output.strip().split('\n')
    clusterRoleBindingName = list(output)

    # 遍历每个 ClusterRoleBinding 名称
    for name in clusterRoleBindingName:
        # 执行 kubectl 命令来获取特定 ClusterRoleBinding 的 json
        get_command = f"kubectl get clusterrolebinding {name}  -o json"
        get_result = subprocess.run(get_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 如果命令成功执行，打印 json 输出
        if get_result.returncode == 0:
            json_output = get_result.stdout.decode('utf-8')
            test_result = validate_cluster_role_binding(json_output)
            if test_result == "00":
                print("\033[1;34;40m", name, "：系统相关的Clusterrolebinding，不进行检查\033[0m")
            elif test_result == "01":
                print("",name, "：ClusterRoleBinding 不允许 Pods/exec 或 pods/attach")
            elif test_result == "02":
                print("\033[1;31;40m", name, "：ClusterRoleBinding 允许 Pods/exec 或 pods/attach\033[0m")
            else:
                print(test_result)
        else:
            print("获取json不成功")
else:
    print("获取clusterrolebinding name不成功")
