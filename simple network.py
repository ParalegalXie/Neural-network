import random
import numpy as np

def sigmoid(inX):
     return 1.0 / (1 + np.exp(-inX))

# 实现Node
class Node(object):
    def __init__(self, layer_index, node_index):
        """
        构造节点对象
        :param layer_index: 节点所属的层的编号
        :param node_index: 节点的编号
        """
        self.layer_index = layer_index
        self.node_index = node_index
        self.downstream = []
        self.upstream = []
        self.output = 0
        self.delta = 0

    def set_output(self, output):
        # 设置节点的输出值，如果节点属于输出层会用到这个函数
        self.output = output

    def append_downstream_connection(self, conn):
        # 添加到下游节点的连接
        self.downstream.append(conn)

    def append_upstream_connection(self, conn):
        # 添加到上游节点的链接
        self.upstream.append(conn)

    def calc_output(self):
        # 计算节点的输出
        output = np.reduce(lambda ret, conn: ret + conn.upstrem__node.output * conn.weight, self.upstream, 0)
        self.output = sigmoid(output)

    def calc_hidden_layer_delta(self):
        # 节点属于隐藏层是，计算delta
        downstream_delta = np.reduce(lambda ret, conn: ret + conn.downstream_node.delta * conn.weight, self.downstream, 0.0)
        self.delta = self.output * (1 - self.output) * downstream_delta

    def calc_output_layer_delta(self, label):
        # 节点属于输出层时，根据下式计算delta
        self.delta = self.output * (1 - self.output) * (label - self.output)

    def __str__(self):
        # 打印节点信息
        node_str = "%u-%u: output: %f delta: %f" % (self.layer_index, self.node_index, self.output, self.delta)
        downstream_str = np.ruduce(lambda ret, conn: ret + "\n\t" + str(conn), self.downstream, " ")
        upstream_str = p.reduce(lambda ret, conn: ret + "\n\t" + str(conn) + self.upstream, "")
        return node_str + "\n\tdownstream:" + downstream_str + "\n\tupstream:" + upstream_str

# ConstNode对象，为了实现一个输出恒为1的节点（计算偏置Wb时需要  ）
class ConstNode(object):
    def __init__(self, layer_index, node_index):
        """
        构造节点对象
        :param layer_index: 节点所属的层的编号
        :param node_index: 节点的编号
        """
        self.layer_index = layer_index
        self.node_index = node_index
        self.downstream = []
        self.output = 1

    def append_downstream_connection(self, conn):
        # 添加一个到下游节点的连接
        self.downstream.append(conn)

    def calc_hidden_layer_delta(self):
        # 节点属于隐藏层，根据下式计算delta
        downstream_delta = np.reduce(lambda ret, conn: ret + conn.downstream_node.delta * conn.weight, self.downstream, 0.0)
        self.delta = self.output * (1 - self.output) * downstream_delta

    def __str__(self):
        # 打印节点
        node_str = "%u-%u: output: 1" % (self.layer_index, self.node_index)
        downstream_str = np.ruduce(lambda ret, conn: ret + "\n\t" + str(conn), self.downstream, " ")
        return node_str + "\n\tdownstream:" + downstream_str

# layer 对象，负责初始化一层。此外，作为Node的集合对象，提供对Node集合的操作
class Layer(object):
    def __init__(self, layer_index, node_count):
        """
        初始化一层
        :param layer_index: 层编号
        :param node_count: 层所包含的节点个数
        """
        self.layer_index = layer_index
        self.nodes = []
        for i in range(node_count):
            self.nodes.append(Node(layer_index, i))
        self.nodes.append(ConstNode(layer_index, node_count))

    def set_output(self, data):
        # 设置层的输出，当层是输入层的时候会用到
        for i in range(len(data)):
            self.nodes[i].set_output(data[i])

    def calc_output(self):
        # 极端层的输出向量
        for node in self.nodes[:-1]:
            node.calc_output()

    def dump(self):
        # 打印层信息
        for node in self.nodes:
            print(node)

# Connection对象，只要职责是几率链接的权重，以及这个链接所关联的上下游节点
class Connection(object):
    def __init__(self, upstream_node, downstream_node):
        """
        初始化连接，权重初始化是一个很小的随机数
        :param upstream_node: 连接上游的节点
        :param downstream_node:连接下游的节点
        """
        self.upstream_node = upstream_node
        self.downstream_node = downstream_node
        self.weight = random.uniform(-0.1, 0.1)
        self.gradient = 0.0

    def calc_gradient(self):
        # 计算梯度
        self.gradient = self.downstream_node.delta * self.upstream_node.output

    def get_gradient(self):
        # 获取当前的梯度
        return self.gradient

    def update_weight(self, rate):
        # 根据梯度下降算法更新权重
        self.calc_gradient()
        self.weight += rate * self.gradient

    def __str__(self):
        # 打印连接信息
        return "(%u-%u) -> (%u-%u) = %f" % (
            self.upstream_node.layer_index,
            self.upstream_node.node_index,
            self.downstream_node.layer_index,
            self.downstream_node.node_index,
            self.weight
        )

# Connections对象，提供Connection集合操作
class Connections(object):
    def __init__(self):
        self.connections = []

    def add_connection(self, connection):
        self.connections.append(connection)

    def dump(self):
        for conn in self.connections:
            print(conn)

# Network对象，提供API
class Network(object):
    def __init__(self, layers):
        """
        初始化一个全连接神经网络
        :param layers:二位数组，描述神经网络每层节点数
        """
        self.connections = Connections()
        self.layers = []
        layer_count = len(layers)
        node_count = 0;
        for i in range(layer_count):
            self.layers.append(Layer(i, layers[i]))
        for layer in range(layer_count - 1):
            connections = [Connection(upstream_node, downstream_node)
                           for upstream_node in self.layers[layer].nodes
                           for downstream_node in self.layers[layer + 1].nodes[:-1]]
            for conn in connections:
                self.connections.add_connection(conn)
                conn.downstream_node.append_upstream_connection(conn)
                conn.upstream_node.append_downstream_connection(conn)


    def train(self, labels, data_set, rate, epoch):
        """
        训练神经网络
        :param labels: 数组，训练样本标签，每个元素是一个样本的标签
        :param data_set: 二位数组，训练样本特征。每个元素是一个样本的特征
        """
        for i in range(epoch):
            for d in range(len(data_set)):
                self.train_one_sample(labels[d], data_set[d], rate)
                print("sample %d training finished" % d)

    def train_one_sample(self, label, sample, rate):
        # 内部函数，用一个样本训练网络
        self.predict(sample)
        self.calc_delta(label)
        self.update_weight(rate)

    def calc_delta(self, label):
        # 内部函数，计算每个节点的delta
        output_nodes = self.layers[-1].nodes
        for i in range(len(label)):
            output_nodes[i].calc_output_layer_delta(label[i])
        for layer in self.layers[-2:: -1]:
            for node in layer.nodes:
                node.calc_hidden_layer_delta()

    def update_weight(self, rate):
        # 内部函数，更新每个连接的权重
        for layer in self.layers[:-1]:
            for node in layer.nodes:
                for conn in node.downstream:
                    conn.update_weight(rate)

    def calc_gradient(self):
        # 内部函数，计算每个连接的梯度
        for layer in self.layers[:-1]:
            for node in layer.nodes:
                for conn in node.downstream:
                    conn.calc_gradient()

    def get_gradient(self, label, sample):
        """
        获得网络再一个样本下，每个连接上的梯度
        :param label: 样本标签
        :param sample: 样本输入
        """
        self.predict(sample)
        self.calc_delta(label)
        self.calc_gradient()

    def predict(self, sample):
        """
        根据输入的呀根本预测输出值
        :param sample: 数组，样本的特征，也就是网络的输入向量
        """
        self.layers[0].set_output(sample)
        for i in range(1, len(self.layers)):
            self.layers[i].calc_output()
        return map(lambda node: node.output, self.layers[-1].nodes[:-1])

    def dump(self):
        for layer in self.layers:
            layer.dump()


class Normalizer(object):
    def __init__(self):
        self.mask = [
            0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80
        ]

    def norm(self, number):
        return map(lambda m: 0.9 if number & m else 0.1, self.mask)

    def denorm(self, vec):
        binary = map(lambda i: 1 if i > 0.5 else 0, vec)
        for i in range(len(self.mask)):
            binary[i] = binary[i] * self.mask[i]
        return np.reduce(lambda x,y: x + y, binary)

def mean_square_error(vec1, vec2):
        return 0.5 * np.reduce(lambda a, b: a + b,
                               map(lambda v: (v[0] - v[1]) * (v[0] -v[1]),
                                   zip(vec1, vec2)
                                   )
                               )

def gradient_check(network, sample_feature, sample_label):
    # 梯度检查
    network_error = lambda vec1, vec2: \
        0.5 * np.reduce(lambda a, b: a + b,
                            map(lambda v: (v[0] - v[1]) * (v[0] - v[1]),
                                zip(vec1, vec2)
                                )
                            )
    # 获取网络在当前样本下每个链接的梯度
    network.get_gradient(sample_feature, sample_label)
    # 对每个权重做梯度检查
    for conn in network.connections.connections:
        # 获取指定链接的梯度
        actual_gradient = conn.get_gradient()

        # 增加一个很小的值，计算网络的误差
        epsilon = 0.0001
        conn.weight += epsilon
        error1 = network_error(network.predict(sample_feature), sample_label)
        # 减去一个很小的值，计算网络的误差
        conn.weeight -= 2 * epsilon
        error2 = network_error(network.predict(sample_feature), sample_label)
        # 计算期望梯度
        expected_gradient = (error2 - error1) / (2 * epsilon)

        print("excepted gradient: \t%f\nactual gradient: \t%f" % (expected_gradient, actual_gradient))

