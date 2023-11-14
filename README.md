# k8s-role-master

## 注意事项

- 每个脚本都能够单独使用，可自行优化，脚本内有详细注释
- 输出内容有添加高亮，更加直观

## 使用说明

使用python3执行main.py

```bash
python3 main.py
```

输入数字选择想要执行的脚本



检测结果展示



## 脚本说明

### clusterrolebindingClusterAdmin.py

检查项：clusterrolebinding是否绑定集群管理员或*的权限

原理：通过kubectl查看clusterrolebinding是否绑定到了cluster-amdin下

输出：

1. 系统相关的Clusterrolebinding，不进行检查

2. ClusterRoleBinding 不引用默认的集群管理员 ClusterRole 或具有通配符权限的 ClusterRole

3. ClusterRoleBinding 引用默认的集群管理员 ClusterRole 或具有通配符权限的 ClusterRole

### clusterrolebindingPodExecAttach.py

检查项：clusterrolebinding是否有pods/exec 或 pods/attach的权限

原理：通过kubectl查看clusterrolebinding是否具有pods/exec 或 pods/attach权限

输出：

1. 系统相关的Clusterrolebinding，不进行检查
2. ClusterRoleBinding 不允许 Pods/exec 或 pods/attach
3. ClusterRoleBinding 允许 Pods/exec 或 pods/attach

### clusterrolePodExecAttach.py

检查项：clusterrole是否有 Pods/exec 或 pods/attach权限

原理：通过kubectl查看clusterrole是否有 pods/exec 或 pods/attach权限

输出：

1. 系统相关的Clusterrole，不进行检查
2. ClusterRole 不允许 Pods/exec 或 pods/attach
3. ClusterRole 允许 Pods/exec 或 pods/attach

### rolebindingServiceaccountPodExecAttach.py

检查项：serviceaccount是否拥有pods/exec 或 pods/attach权限

原理：通过kubectl查看rolebinding从而查找到绑定的serviceaccount和role，查看role是否拥有Pods/exec 或 pods/attach权限

输出：

1. 系统相关的serviceaccount，不进行检查

2. 没有serviceaccount，不进行检查
3. serviceaccount不允许 pods/exec 或 pods/attach
4. serviceaccount允许 pods/exec 或 pods/attach

### rolePodExecAttach.py

检查项：role是否拥有pods/exec 或 pods/attach权限

原理：通过kubectl查看role是否拥有pods/exec 或 pods/attach权限

输出：

1. 系统相关的role，不进行检查

2. role不允许 pods/exec 或 pods/attach
3. role允许 pods/exec 或 pods/attach
