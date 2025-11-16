from app.models.user_output import UserOutput
from app.tools.base_interpreter import BaseCodeInterpreter
from app.core.agents.modeler_agent import ModelerToCoder


class Flows:
    def __init__(self, questions: dict[str, str | int], language: str = "zh", work_dir: str | None = None):
        self.flows: dict[str, dict] = {}
        self.questions: dict[str, str | int] = questions
        self.language = language
        self.work_dir = work_dir

    def set_flows(self, ques_count: int):
        ques_str = [f"ques{i}" for i in range(1, ques_count + 1)]
        seq = [
            "firstPage",
            "RepeatQues",
            "analysisQues",
            "modelAssumption",
            "symbol",
            "eda",
            *ques_str,
            "sensitivity_analysis",
            "judge",
        ]
        self.flows = {key: {} for key in seq}

    def get_solution_flows(
        self, questions: dict[str, str | int], modeler_response: ModelerToCoder
    ):
        questions_quesx = {
            key: value
            for key, value in questions.items()
            if key.startswith("ques") and key != "ques_count"
        }
        
        # Bilingual prompts
        if self.language == "en":
            ques_template = "Refer to the solution provided by the modeler: {solution}\nComplete the following problem: {problem}"
            data_files_with = "Dataset files: {files}"
            data_files_without = "Please use the list_files tool to view data files in the current directory"
            eda_template = "Refer to the solution provided by the modeler: {solution}\n{data_info}\nPerform EDA analysis (data cleaning, visualization) on the data in the current directory, save cleaned data to the current directory, **no complex models needed**"
            sensitivity_template = "Refer to the solution provided by the modeler: {solution}\nComplete sensitivity analysis"
        else:
            ques_template = "参考建模手给出的解决方案{solution}\n完成如下问题{problem}"
            data_files_with = "数据集文件: {files}"
            data_files_without = "请使用list_files工具查看当前目录下的数据文件"
            eda_template = "参考建模手给出的解决方案{solution}\n{data_info}\n对当前目录下数据进行EDA分析(数据清洗,可视化),清洗后的数据保存当前目录下,**不需要复杂的模型**"
            sensitivity_template = "参考建模手给出的解决方案{solution}\n完成敏感性分析"
        
        ques_flow = {
            key: {
                "coder_prompt": ques_template.format(
                    solution=modeler_response.questions_solution[key],
                    problem=value
                ),
            }
            for key, value in questions_quesx.items()
        }
        
        # 获取当前目录下的数据集文件
        from app.utils.common_utils import get_current_files
        import os
        data_files = []
        try:
            work_dir = self.work_dir or os.path.join("project", "work_dir")
            if work_dir and os.path.exists(work_dir) and os.path.isdir(work_dir):
                data_files = get_current_files(work_dir, "data")
        except Exception:
            # 如果获取失败，让agent自己去list_files
            pass
        
        if data_files:
            data_files_info = data_files_with.format(files=', '.join(data_files))
        else:
            data_files_info = data_files_without
        
        flows = {
            "eda": {
                "coder_prompt": eda_template.format(
                    solution=modeler_response.questions_solution["eda"],
                    data_info=data_files_info
                ),
            },
            **ques_flow,
            "sensitivity_analysis": {
                "coder_prompt": sensitivity_template.format(
                    solution=modeler_response.questions_solution["sensitivity_analysis"]
                ),
            },
        }
        return flows

    def get_write_flows(
        self, user_output: UserOutput, config_template: dict, bg_ques_all: str
    ):
        model_build_solve = user_output.get_model_build_solve()
        flows = {
            "firstPage": f"""问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["firstPage"]}，撰写标题，摘要，关键词""",
            "RepeatQues": f"""问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["RepeatQues"]}，撰写问题重述""",
            "analysisQues": f"""问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["analysisQues"]}，撰写问题分析""",
            "modelAssumption": f"""问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["modelAssumption"]}，撰写模型假设""",
            "symbol": f"""不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["symbol"]}，撰写符号说明部分""",
            "judge": f"""不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["judge"]}，撰写模型的评价部分""",
        }
        return flows

    def get_writer_prompt(
        self,
        key: str,
        coder_response: str,
        code_interpreter: BaseCodeInterpreter,
        config_template: dict,
    ) -> str:
        """根据不同的key生成对应的writer_prompt

        Args:
            key: 任务类型
            coder_response: 代码执行结果

        Returns:
            str: 生成的writer_prompt
        """
        code_output = code_interpreter.get_code_output(key)

        questions_quesx_keys = self.get_questions_quesx_keys()
        bgc = self.questions["background"]
        quesx_writer_prompt = {
            key: f"""
                    问题背景{bgc},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template[key]}
                """
            for key in questions_quesx_keys
        }

        writer_prompt = {
            "eda": f"""
                    问题背景{bgc},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template["eda"]}
                """,
            **quesx_writer_prompt,
            "sensitivity_analysis": f"""
                    问题背景{bgc},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template["sensitivity_analysis"]}
                """,
        }

        if key in writer_prompt:
            return writer_prompt[key]
        else:
            raise ValueError(f"未知的任务类型: {key}")

    def get_questions_quesx_keys(self) -> list[str]:
        """获取问题1,2...的键"""
        return list(self.get_questions_quesx().keys())

    def get_questions_quesx(self) -> dict[str, str]:
        """获取问题1,2,3...的键值对"""
        # 获取所有以 "ques" 开头的键值对
        questions_quesx = {
            key: value
            for key, value in self.questions.items()
            if key.startswith("ques") and key != "ques_count"
        }
        return questions_quesx

    def get_seq(self, ques_count: int) -> dict[str, str]:
        ques_str = [f"ques{i}" for i in range(1, ques_count + 1)]
        seq = [
            "firstPage",
            "RepeatQues",
            "analysisQues",
            "modelAssumption",
            "symbol",
            "eda",
            *ques_str,
            "sensitivity_analysis",
            "judge",
        ]
        return {key: "" for key in seq}
