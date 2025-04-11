#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from user_data_operations import get_team_members

if __name__ == "__main__":
    if len(sys.argv) > 1:
        group_id = sys.argv[1]
        get_team_members(group_id)
    else:
        print("请提供组号参数")
