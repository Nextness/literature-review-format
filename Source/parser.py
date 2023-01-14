import regex as re
from dataclasses import dataclass, field
from json import dumps
from typing import (
    Union,
    Any,
    Optional,
    Callable
)

def j_print(dictonary: dict) -> None:
        
    indent = 4
    ensure_ascii = False
    print(dumps(dictonary, indent=indent, ensure_ascii=ensure_ascii))


def removeLC(inputString: str) -> str:
    pattern = re.compile(r'//.*?$', re.DOTALL)
    return re.sub(
        pattern = pattern,
        repl = "",
        string = inputString.strip()
    )


class RESERVED:
    ENTRY_TYPE = r"Entry"
    END_ENTRY = r"End"
    RELEVANCE = r"(main|notable)"
    DATATYPE_TYPE = r"(string|int|bool)"
    RESTRICITED_WORDS = r"(key|cluster)"
    INPUT = r"(\"[\d\s\w\.\-\:]+\"|\d+|false|true|undefined|null)" # \"[\w\d\s]+\"|
    NULL = r"null"
    PARAMETERS = r"UNKEY"
    OPERATOR = r"\-\>"

def format_data(string: str, remove_list: list[Any]) -> list[str]:
    string = string.strip()
    for item in remove_list:
        string = re.sub(item, "", string)
    string = string.split(" ")
    return list(filter(None, string))

def format_data_title(string: str, remove_list: list[Any]) -> list[str]:
    string = string.strip()
    for item in remove_list:
        string = re.sub(item, "", string)
    string = string.split(" ", 2)
    return list(filter(None, string))


@dataclass
class EntryDeserialization:
    Constructor: Any = field(repr=False)
    EntryRelevance: str = field(init=False)
    EntryType: str = field(init=False)
    UniqueIDKey: str = field(init=False)
    UniqueIDValue: str = field(init=False)

    def __post_init__(self):
        remove_list: list = [
            RESERVED.ENTRY_TYPE,
            RESERVED.DATATYPE_TYPE,
            RESERVED.RESTRICITED_WORDS,
            r"\(|\:|\)|\{|\n|\""
        ]

        self.Constructor = format_data(self.Constructor, remove_list)
        self.EntryRelevance = self.Constructor[0]
        self.EntryType = self.Constructor[1]
        self.UniqueIDKey = self.Constructor[2]
        self.UniqueIDValue = self.Constructor[3]

def is_data_entry(input_string: list[str]) -> bool:
    input_string: str = input_string[0].strip()
    entry_pattern_regex = f'{RESERVED.ENTRY_TYPE}\({RESERVED.RELEVANCE}\s+[\d\w]+:\s+{RESERVED.RESTRICITED_WORDS}\s+[\d\w]+\s+{RESERVED.DATATYPE_TYPE}\s+"[\w\d\.\/\-]+"\)\s*{{'
    return True if re.match(entry_pattern_regex, input_string) else False


@dataclass
class keyObject:
    Constructor: Any = field(repr=False)
    Key: str = field(init=False)
    Value: str = field(init=False)

    def __post_init__(self):
        remove_list: list = [
            RESERVED.RESTRICITED_WORDS,
            RESERVED.DATATYPE_TYPE,
            r"\"|\;"
        ]
        # TODO: Fix this horrible code. :(
        if "kv_field Title" in self.Constructor: 
            self.Constructor = format_data_title(self.Constructor, remove_list)
        else:
            self.Constructor = format_data(self.Constructor, remove_list)
        self.Key = self.Constructor[0].strip()
        self.Value = self.Constructor[1].strip()

def is_kv_field(input_string: list[str]) -> bool:
    input_string: str = input_string[0].strip()
    kv_field_pattern_regex = f'{RESERVED.RESTRICITED_WORDS}\s+[\w\d]+\s+{RESERVED.DATATYPE_TYPE}\s+{RESERVED.INPUT};'
    return True if re.match(kv_field_pattern_regex, input_string) else False


@dataclass
class ClusterObject:
    Constructor: Any = field(repr=False)
    ClusterName: str = field(init=False)
    Unkey: bool = field(default=False, init=False)
    EntryDataDict: Optional[dict[str]] = field(default=None, init=False)
    EntryDataList: Optional[list[str]] = field(default=None, init=False)


    def __post_init__(self):
        _regex_remove_string: str = f'{RESERVED.RESTRICITED_WORDS}|\{{|\s' 
        _regex_null_cluster = f'{RESERVED.RESTRICITED_WORDS}\s+[\d\w]+\s+{RESERVED.NULL};'
        self.Constructor = re.sub(pattern = _regex_remove_string, repl = "", string = self.Constructor)
        
        if self.Constructor.endswith("null;"):
            self.ClusterName = re.sub(pattern= f'{RESERVED.NULL}', repl = "", string = self.Constructor)
            self.Unkey = RESERVED.NULL

        elif "->" in self.Constructor:
            self.Constructor = self.Constructor.split("->")
            self.ClusterName = self.Constructor[0]
            if self.Constructor[1].casefold() == "unkey":
                self.Unkey = True
                self.EntryDataList = list()
                
        elif self.Constructor:
            self.ClusterName = self.Constructor
            self.EntryDataDict = dict()

def is_cluster(input_string: list[str]) -> bool:
    input_string: str = input_string[0].strip()
    cluster_pattern_regex_1: str = f'({RESERVED.RESTRICITED_WORDS}\s+[\d\w]+\s+{{)|({RESERVED.RESTRICITED_WORDS}\s+[\d\w]+\s+{RESERVED.OPERATOR}\s+{RESERVED.PARAMETERS}\s+{{)|({RESERVED.RESTRICITED_WORDS}\s+[\d\w]+\s+{RESERVED.NULL}\;)'
    return True if re.match(f'{cluster_pattern_regex_1}', input_string) else False


@dataclass
class UnkeyEntry:
    Constructor: Any = field(repr=False)
    Value: Union[str, int, bool, None] = field(init=False)

    def __post_init__(self):
        _regex_remove_string: str = f'{RESERVED.DATATYPE_TYPE}|\"|\;'
        self.Constructor = re.sub(pattern = _regex_remove_string, repl = "", string = self.Constructor)
        self.Value = str(self.Constructor.strip())

def is_unkey_entry(input_string: str) -> bool:
    input_string: str = input_string[0].strip()
    unkey_entry_pattern_regex: str = f'{RESERVED.DATATYPE_TYPE}\s+{RESERVED.INPUT};'
    return True if re.match(unkey_entry_pattern_regex, input_string) else False


# TODO: Include error handling when parsing the file
# TODO: Include removal of single line comment
# TODO: Remove debug code from the funciton
# TODO: Separate function definitions into their appropriate places.
# TODO: Take a look at the recursion, it looks bugged. Also make it better because right now it looks like crap :)

def literature_review_parser(
    *, fileData: list[str], 
    dictionaryObject: dict = dict()
) -> dict[str, Any]:
    
    debug_counter = 0

    def constructNestedDict(
        *, _internalReturnDictionary: dict[Any],
        _DictionaryObjectConstructorList: list[str],
        _internalInsertValue: Any,
        _setInputType: Union[Callable, None],
        _popLastElementList: bool = False,
    ) -> dict[Any]:

        tmpDict = _internalReturnDictionary
        for item in _DictionaryObjectConstructorList[:-1]:
            tmpDict = tmpDict[item]
        
        if _setInputType == RESERVED.NULL:
            tmpDict[_DictionaryObjectConstructorList[-1]] = _internalInsertValue
            
        elif isinstance(_setInputType, dict):
            tmpDict.update({
                _DictionaryObjectConstructorList[-1]: _internalInsertValue
            })

        elif isinstance(_setInputType, list):
            tmpDict[_DictionaryObjectConstructorList[-1]].append(_internalInsertValue)

        if _popLastElementList: _DictionaryObjectConstructorList.pop()
        return _internalReturnDictionary
    
    def parseDataEntry(
        *, fileData: list[str], 
        _internalReturnDictionary: dict
    ) -> tuple[dict[str, str], list[str]]:

        entryKey: str = "entryInformation"
        inputString: str = removeLC(fileData[0])
        dataEntry: EntryDeserialization = EntryDeserialization(
            Constructor = inputString
        )

        _internalUniqueID: str = f"({dataEntry.UniqueIDKey}): {dataEntry.UniqueIDValue}"
        _internalReturnDictionary.update({
            _internalUniqueID: {
                dataEntry.EntryRelevance: dataEntry.EntryType,
                entryKey: dict()
            }
        })

        _DictionaryObjectConstructorList: list[str] =[
            _internalUniqueID,
            entryKey
        ]

        fileData.pop(0)
        return _internalReturnDictionary, _DictionaryObjectConstructorList


    def parseKeyField(
        *, fileData: list[str],  
        _internalReturnDictionary: dict, 
        _DictionaryObjectConstructorList: list[str]
    ) -> tuple[dict[str, str], list[str]]:
        
        inputString: str = removeLC(fileData[0])
        KeyField: keyObject = keyObject(Constructor = inputString)
        _DictionaryObjectConstructorList.append(
            KeyField.Key
        )

        _internalReturnDictionary: dict = constructNestedDict(
            _internalReturnDictionary = _internalReturnDictionary,
            _DictionaryObjectConstructorList = _DictionaryObjectConstructorList,
            _internalInsertValue = KeyField.Value,
            _setInputType = dict(),
            _popLastElementList = True
        )

        fileData.pop(0)
        return _internalReturnDictionary, _DictionaryObjectConstructorList

    def parseUnkeyEntry(
        *, fileData: list[str],
        _internalReturnDictionary: dict, 
        _DictionaryObjectConstructorList: list[str]
    ) -> dict[Any]:

        inputString: str = removeLC(fileData[0])
        unkeyEntry: UnkeyEntry = UnkeyEntry(Constructor = inputString)
        _internalReturnDictionary: dict = constructNestedDict(
            _internalReturnDictionary = _internalReturnDictionary,
            _DictionaryObjectConstructorList = _DictionaryObjectConstructorList,
            _setInputType = list(),
            _internalInsertValue = unkeyEntry.Value
        )

        fileData.pop(0)
        return _internalReturnDictionary

    def parseCluster(
        *, fileData: list[str],
        _internalReturnDictionary: dict, 
        _DictionaryObjectConstructorList: list[str]
    ) -> tuple[dict[str, str], list[str]]:
        
        inputString: str = removeLC(fileData[0])
        cluster: ClusterObject = ClusterObject(Constructor = inputString)

        fileData.pop(0)
        _DictionaryObjectConstructorList.append(
            cluster.ClusterName
        )

        if (cluster.EntryDataDict is None) and (cluster.EntryDataList is None) and (cluster.Unkey == RESERVED.NULL):
            _internalReturnDictionary: dict = constructNestedDict(
                _internalReturnDictionary = _internalReturnDictionary,
                _DictionaryObjectConstructorList = _DictionaryObjectConstructorList,
                _setInputType = RESERVED.NULL,
                _internalInsertValue = cluster.ClusterName
            )
            _DictionaryObjectConstructorList.pop()

        elif cluster.Unkey and isinstance(cluster.EntryDataList, list):
            _internalReturnDictionary: dict = constructNestedDict(
                _internalReturnDictionary = _internalReturnDictionary,
                _DictionaryObjectConstructorList = _DictionaryObjectConstructorList,
                _setInputType = dict(),
                _internalInsertValue = []
            )
            while True:
                if fileData[0].strip().startswith("}"): break
                _internalReturnDictionary = parseUnkeyEntry(
                    fileData = fileData, _internalReturnDictionary = _internalReturnDictionary,
                    _DictionaryObjectConstructorList = _DictionaryObjectConstructorList
                )
                
            _DictionaryObjectConstructorList.pop()

        elif not cluster.Unkey and isinstance(cluster.EntryDataDict, dict):
            if is_kv_field(fileData):
                _internalReturnDictionary: dict = constructNestedDict(
                    _internalReturnDictionary = _internalReturnDictionary,
                    _DictionaryObjectConstructorList = _DictionaryObjectConstructorList,
                    _setInputType = dict(),
                    _internalInsertValue = dict()
                )

                while True:
                    if fileData[0].strip().startswith("}"): 
                        fileData.pop(0)
                        break
                    _internalReturnDictionary, dictionaryObjectConstructorList = parseKeyField(
                        fileData = fileData, _internalReturnDictionary = _internalReturnDictionary,
                        _DictionaryObjectConstructorList = _DictionaryObjectConstructorList
                    )
            
                _DictionaryObjectConstructorList.pop()


            elif is_cluster(fileData):
                _internalReturnDictionary, _DictionaryObjectConstructorList = parseCluster(
                    fileData = fileData, _internalReturnDictionary = _internalReturnDictionary,
                    _DictionaryObjectConstructorList = _DictionaryObjectConstructorList
                )

        return _internalReturnDictionary, _DictionaryObjectConstructorList
    
    while fileData:

        if is_data_entry(fileData):
            dictionaryObject, dictionaryObjectConstructorList = parseDataEntry(
                fileData = fileData, _internalReturnDictionary = dictionaryObject
            )
        
        elif is_kv_field(fileData):
            dictionaryObject, dictionaryObjectConstructorList = parseKeyField(
                fileData = fileData, _internalReturnDictionary = dictionaryObject,
                _DictionaryObjectConstructorList = dictionaryObjectConstructorList
            )

        elif is_cluster(fileData):
            dictionaryObject, dictionaryObjectConstructorList = parseCluster(
                fileData = fileData,
                _internalReturnDictionary = dictionaryObject,
                _DictionaryObjectConstructorList = dictionaryObjectConstructorList
            )

        elif fileData[0].strip().startswith("} @END;"):
            dictionaryObjectConstructorList = list()
            fileData.pop(0)

        elif fileData[0].strip().startswith("}"):
            fileData.pop(0)
        
        else:
            fileData.pop(0)


        debug_counter += 1

    return dictionaryObject
