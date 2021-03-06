import json
import yaml
import logging
import os
import shutil
from SwaggerToCase.encoder import JSONEncoder
from backend.models.models import Project, TestCase, Config, StepCase, API, Validate, Extract, Parameters, \
    VariablesLocal, DebugTalk


class DumpFile(object):
    def __init__(self, config, test_apis, test_cases):
        self.testcase_dir = config["testcase_dir"]
        self.api_file = config["api_file"]
        self.file_type = config["file_type"]
        self.env_file = config["env_file"]
        self.code_file = config["code_file"]
        self.test_apis = test_apis
        self.test_cases = test_cases

    def dump_api_file(self):
        if self.file_type == "YAML":
            api_file = os.path.join(self.api_file, '{}.{}'.format(self.api_file, 'yml'))
            logging.debug("Start to generate YAML apis.")
            with open(api_file, 'w', encoding="utf-8") as outfile:
                yaml.dump(self.test_apis, outfile, allow_unicode=True, default_flow_style=False, indent=4)
            logging.debug("Generate YAML api_file successfully: {}".format(self.api_file))
        else:
            api_file = os.path.join(self.api_file, '{}.{}'.format(self.api_file, 'json'))
            logging.debug("Start to generate JSON apis.")
            with open(api_file, 'w', encoding="utf-8") as outfile:
                my_json_str = json.dumps(self.test_apis, ensure_ascii=False, indent=4, cls=JSONEncoder, sort_keys=True)
                if isinstance(my_json_str, bytes):
                    my_json_str = my_json_str.decode("utf-8")
                outfile.write(my_json_str)
            logging.debug("Generate JSON api_file successfully: {}".format(self.api_file))

    def dump_testcases_files(self):
        if not os.path.exists(self.testcase_dir):
            os.mkdir(self.testcase_dir)
        else:
            shutil.rmtree(self.testcase_dir)
            os.mkdir(self.testcase_dir)

        for name, case in self.test_cases:
            # 将对象先转换成json字符串，进行strip去除一些杂质字符，再转回obj
            case_json = json.dumps(case)
            case_json = case_json.strip()
            case = json.loads(case_json)
            if self.file_type == 'YAML':
                case_path = os.path.join(self.testcase_dir, '{}.{}'.format(name, 'yml'))
                logging.debug("Start to generate YAML testcases.")
                with open(case_path, 'w', encoding="utf-8") as outfile:
                    yaml.dump(case, outfile, allow_unicode=True, default_flow_style=False, indent=2)
                logging.debug("Generate YAML testcase successfully: {}".format(case_path))
            else:
                case_path = os.path.join(self.testcase_dir, '{}.{}'.format(name, 'json'))
                with open(case_path, 'w', encoding="utf-8") as outfile:
                    my_json_str = json.dumps(case, ensure_ascii=False, indent=4, cls=JSONEncoder, sort_keys=True)
                    if isinstance(my_json_str, bytes):
                        my_json_str = my_json_str.decode("utf-8")
                    outfile.write(my_json_str)
                logging.debug("Generate JSON testcase successfully: {}".format(case_path))

    def dump_env_file(self, env_content):
        with open(self.env_file, 'w', encoding="utf-8") as outfile:
            outfile.write(env_content)
        logging.debug("Generate env_file successfully: {}".format(self.env_file))

    def dump_code_file(self, code_content):
        with open(self.code_file, 'w', encoding="utf-8") as outfile:
            outfile.write(code_content)
        logging.debug("Generate code_file successfully: {}".format(self.code_file))

    def dump_to_file(self):
        self.dump_api_file()  # 写入api文件
        self.dump_testcases_files()  # 写入testcase文件


class DumpDB(object):
    def __init__(self, test_apis, test_cases, session):
        self.test_apis = test_apis
        self.test_cases = test_cases
        self.session = session

    def insert_extract(self, step, step_obj):
        step_case = step["test"]
        extract = step_case.get("extract", None)
        if extract is not None:
            extract_list = extract
            for item in extract_list:
                key, value = tuple(item.items())[0]
                extract_obj = Extract(key=key, value=value, stepcase_id=step_obj.id)
                self.session.add(extract_obj)
                self.session.commit()

    def insert_validate(self, step, step_obj):
        validate_list = step["test"]["validate"]
        for item in validate_list:
            key, value = tuple(item.items())[0]
            comparator = key
            check = value[0]
            expected = value[1]
            if isinstance(expected, int):
                expected_type = "int"
            else:
                expected_type = "str"
            validate_obj = Validate(comparator=comparator,
                                    check=check,
                                    expected=expected,
                                    expected_type=expected_type,
                                    stepcase_id=step_obj.id)
            self.session.add(validate_obj)
            self.session.commit()

    def insert_api(self, project_obj):
        for api in self.test_apis:
            test_api = api["api"]
            api_func = test_api["def"]
            request = test_api["request"]
            url = request["url"]
            method = request["method"]
            body = json.dumps(api)
            api_obj = API(api_func=api_func, url=url, method=method, body=body, project_id=project_obj.id)
            self.session.add(api_obj)
            self.session.commit()

    def insert_stepcase(self, step, case_obj):
        step_case = step["test"]
        name = step_case["name"]
        api_name = step_case["api"]
        step_obj = StepCase(name=name,
                            step=1,
                            api_name=api_name,
                            testcase_id=case_obj.id)
        self.session.add(step_obj)
        self.session.commit()
        return step_obj

    def insert_parameters(self, config, config_obj):
        config_field = config["config"]
        parameters = config_field.get("parameters")
        for item in parameters:
            key, value = tuple(item.items())[0]
            try:
                value = json.loads(value)
                value_type = "json_list"
            except Exception as e:
                value_type = "defined_func"
            parameter_obj = Parameters(key=key,
                                       value=value,
                                       value_type=value_type,
                                       config_id=config_obj.id)
            self.session.add(parameter_obj)
            self.session.commit()

    def insert_variables_local(self, step, case_obj):
        variables = step["test"]["variables"]
        for item in variables:
            key, value = tuple(item.items())[0]
            # 其实经swagger2case的maker只有json类型
            # 这里时为了规范，后面也要用到类似的逻辑
            # 其实variables_global也应该有insert_variables_global，但是swagger2case没有global
            if isinstance(value, int):
                value_type = "int"
            else:
                try:
                    int(value)
                    value_type = "json"  # "123"/"[1,2,3]" 也是json的一种
                except Exception as e:
                    try:
                        value = json.dumps(value)
                        value_type = "json"
                    except Exception as e:
                        value_type = "str"
            variable_obj = VariablesLocal(key=key,
                                          value=value,
                                          value_type=value_type,
                                          stepcase_id=case_obj.id)
            self.session.add(variable_obj)
            self.session.commit()

    def insert_config(self, config, case_obj):
        name = config["config"]["name"]
        body = json.dumps(config)
        config_obj = Config(name=name, body=body, testcase_id=case_obj.id)
        self.session.add(config_obj)
        self.session.commit()
        return config_obj

    def insert_testcase(self, case_name, project_obj):
        case_obj = TestCase(name=case_name, project_id=project_obj.id)
        self.session.add(case_obj)
        self.session.commit()
        return case_obj

    def insert_project(self, project):
        # insert into project
        name = project["name"]
        if project["url"]:
            mode = "url"
        else:
            mode = "file"
        desc = project["desc"]
        owner = project["owner"]
        project_obj = Project(name=name, mode=mode, desc=desc, owner=owner)
        self.session.add(project_obj)
        self.session.commit()
        debugtalk_obj = DebugTalk(
            code="# drive code for your project",
            project_id=project_obj.id
        )
        self.session.add(debugtalk_obj)
        self.session.commit()

        # insert into testcase
        for case in self.test_cases:
            case_name, test_case = case
            case_obj = self.insert_testcase(case_name, project_obj)
            config = test_case[0]
            config_obj = self.insert_config(config, case_obj)
            # insert_parameters没什么意义，初始parameters为空列表
            self.insert_parameters(config, config_obj)
            for step in test_case[1:]:
                step_obj = self.insert_stepcase(step, case_obj)
                self.insert_variables_local(step, step_obj)
                self.insert_validate(step, step_obj)
                # insert_parameters没什么意义，初始extract为空列表
                self.insert_extract(step, step_obj)

        # insert into test_api
        self.insert_api(project_obj)

    def dump_to_db(self, config):
        project = config["project"]
        self.insert_project(project)

