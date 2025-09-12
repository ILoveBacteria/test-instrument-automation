from robot.api import get_model
from robot.parsing.model.blocks import TestCaseSection, SettingSection, TestCase
from robot.parsing.model.statements import KeywordCall, Documentation


class MyKeyword:
    def __init__(self, name: str, lineno: int):
        self.name = name
        self.lineno = lineno

    def to_dict(self):
        return {
            'name': self.name,
            'lineno': self.lineno
        }


class MyTestCase:
    def __init__(self, name: str, lineno: int):
        self.name = name
        self.lineno = lineno
        self.keywords: list[MyKeyword] = []
        self.documentation: str = None

    def to_dict(self):
        return {
            'name': self.name,
            'lineno': self.lineno,
            'documentation': self.documentation,
            'keywords': [kw.to_dict() for kw in self.keywords]
        }


class MyTestSuite:
    def __init__(self, name: str):
        self.name = name
        self.libraries: list[str] = []
        self.testcases: list[MyTestCase] = []

    def to_dict(self):
        return {
            'name': self.name,
            'libraries': self.libraries,
            'testcases': [tc.to_dict() for tc in self.testcases]
        }

    @classmethod
    def from_file(cls, path: str):
        model = get_model(path)
        suite = cls(name=path)

        for section in model.sections:
            # Collect libraries
            if isinstance(section, SettingSection):
                for lib in section.body:
                    if lib.type == 'LIBRARY':
                        suite.libraries.append(lib.name)

            # Collect test cases + their keywords
            elif isinstance(section, TestCaseSection):
                for test in section.body:
                    if not isinstance(test, TestCase):
                        continue
                    tc = MyTestCase(test.name, test.lineno)
                    for step in test.body:
                        if isinstance(step, KeywordCall):
                            tc.keywords.append(
                                MyKeyword(step.keyword, step.lineno)
                            )
                        elif isinstance(step, Documentation):
                            tc.documentation = step.value
                    suite.testcases.append(tc)

        return suite
