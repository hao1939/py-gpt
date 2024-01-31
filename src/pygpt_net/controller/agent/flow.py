#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.31 20:00:00                  #
# ================================================== #

from pygpt_net.item.ctx import CtxItem
from pygpt_net.utils import trans


class Flow:
    def __init__(self, window=None):
        """
        Agent flow controller

        :param window: Window instance
        """
        self.window = window
        self.iteration = 0
        self.prev_output = None
        self.is_user = True
        self.stop = False
        self.allowed_cmds = [
            "goal_update",
        ]

    def on_system_prompt(
            self,
            prompt: str,
            append_prompt: str = "",
            auto_stop: bool = True,
    ) -> str:
        """
        Event: On prepare system prompt

        :param prompt: prompt
        :param append_prompt: extra prompt (instruction)
        :param auto_stop: auto stop
        :return: updated prompt
        """
        stop_cmd = ""
        if auto_stop:
            stop_cmd = '\n\nON FINISH: When you believe that the task has been completed 100% and all goals have ' \
                       'been achieved, include the following command in your response, which will stop further ' \
                       'conversation. Remember to put it in the form as given, at the end of response and including ' \
                       'the surrounding ~###~ marks: ~###~{"cmd": "goal_update", "params": {"status": "finished"}}~###~'

        # select prompt to use
        if append_prompt is not None and append_prompt.strip() != "":
            append_prompt = "\n" + append_prompt
        prompt += str(append_prompt) + stop_cmd
        return prompt

    def on_input_before(self, prompt: str) -> str:
        """
        Event: On user input before

        :param prompt: prompt
        :return: updated prompt
        """
        if not self.is_user:
            return prompt

        return "user: " + prompt

    def on_user_send(self, text: str):
        """
        Event: On user send text

        :param text: text
        """
        self.iteration = 0
        self.prev_output = None
        self.is_user = True
        if self.stop:
            self.stop = False
        self.window.controller.agent.update()  # update status

    def on_ctx_end(
            self,
            ctx: CtxItem,
            iterations: int = 0,
    ):
        """
        Event: On context end

        :param ctx: CtxItem
        :param iterations: iterations
        """
        if self.stop:
            self.stop = False
            self.iteration = 0
            self.prev_output = None
            self.window.controller.agent.update()  # update status

        if iterations == 0 or self.iteration < int(iterations):
            self.iteration += 1
            self.window.controller.agent.update()  # update status
            if self.prev_output is not None and self.prev_output != "":
                self.window.controller.chat.input.send(
                    self.prev_output,
                    force=True,
                    internal=True,
                )
                # internal call will not trigger async mode and will hide the message from previous iteration

    def on_ctx_before(
            self,
            ctx: CtxItem,
            reverse_roles: bool = False,
    ):
        """
        Event: Before ctx

        :param ctx: CtxItem
        :param reverse_roles: reverse roles
        """
        ctx.internal = True  # always force internal call
        self.is_user = False
        if self.iteration == 0:
            ctx.first = True

        # reverse roles in ctx
        if self.iteration > 0 \
                and self.iteration % 2 != 0 \
                and reverse_roles:
            tmp_input_name = ctx.input_name
            tmp_output_name = ctx.output_name
            ctx.input_name = tmp_output_name
            ctx.output_name = tmp_input_name

    def on_ctx_after(self, ctx: CtxItem):
        """
        Event: After ctx

        :param ctx: CtxItem
        """
        self.prev_output = ctx.output

    def on_cmd(
            self,
            ctx: CtxItem,
            cmds: list,
    ):
        """
        Event: On commands

        :param ctx: CtxItem
        :param cmds: commands dict
        """
        if self.window.core.config.get('agent.auto_stop'):
            self.cmd(ctx, cmds)

    def cmd(
            self,
            ctx: CtxItem,
            cmds: list,
    ):
        """
        Event: On command

        :param ctx: CtxItem
        :param cmds: commands dict
        """
        is_cmd = False
        my_commands = []
        for item in cmds:
            if item["cmd"] in self.allowed_cmds:
                my_commands.append(item)
                is_cmd = True

        if not is_cmd:
            return

        for item in my_commands:
            try:
                if item["cmd"] == "goal_update":
                    if item["params"]["status"] == "finished":
                        self.on_stop()
                        self.window.ui.status(trans('status.finished'))  # show info
            except Exception as e:
                self.window.core.debug.error(e)
                return

    def on_stop(self):
        """
        Event: On force stop
        """
        self.iteration = 0
        self.prev_output = None
        self.stop = True