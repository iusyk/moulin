# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 EPAM Systems
"""
Android open source project (AOSP) builder module
"""

import os.path
from typing import List
from yaml.nodes import MappingNode
from moulin import yaml_helpers as yh
from moulin import ninja_syntax


def get_builder(conf: MappingNode, name: str, build_dir: str, src_stamps: List[str],
                generator: ninja_syntax.Writer):
    """
    Return configured AndroidBuilder class
    """
    return AndroidBuilder(conf, name, build_dir, src_stamps, generator)


def gen_build_rules(generator: ninja_syntax.Writer):
    """
    Generate yocto build rules for ninja
    """
    cmd = " && ".join([
        "export $env",
        "cd $build_dir",
        "source build/envsetup.sh",
        "lunch $lunch_target",
        "m -j",
    ])
    generator.rule("android_build",
                   command=f'bash -c "{cmd}"',
                   description="Invoke Android build system",
                   pool="console")
    generator.newline()


class AndroidBuilder:
    """
    AndroidBuilder class generates Ninja rules for given Android build configuration
    """
    def __init__(self, conf: MappingNode, name: str, build_dir: str, src_stamps: List[str],
                 generator: ninja_syntax.Writer):
        self.conf = conf
        self.name = name
        self.generator = generator
        self.src_stamps = src_stamps
        self.build_dir = build_dir

    def gen_build(self):
        """Generate ninja rules to build AOSP"""
        env_node = yh.get_sequence_node(self.conf, "env")
        if env_node:
            env_values = [x.value for x in env_node.value]
        else:
            env_values = []
        env = " ".join(env_values)
        variables = {
            "build_dir": self.build_dir,
            "env": env,
            "lunch_target": yh.get_mandatory_str_value(self.conf, "lunch_target")[0]
        }
        targets = [
            os.path.join(self.build_dir, t.value)
            for t in yh.get_mandatory_sequence(self.conf, "target_images")
        ]
        self.generator.build(targets, "android_build", self.src_stamps, variables=variables)
        self.generator.newline()

        return targets

    def capture_state(self):
        """
        This method should capture Android state for a reproducible builds.
        Luckily, there is nothing to do, as Android state is controlled solely by
        its repo state. And repo state is captured by repo fetcher code.
        """
