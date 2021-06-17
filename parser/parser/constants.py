"""
From:
https://www.ibm.com/docs/en/i/7.3?topic=extensions-standard-c-library-functions-table-by-name
https://www.cplusplus.com/reference/iolibrary/#:~:text=A%20stream%20is%20an%20abstraction,and%20ouput%20operations%20are%20performed.&text=For%20example%2C%20file%20streams%20are,physically%20reflected%20in%20the%20file.
https://www.cprogramming.com/function.html

It's necessary to keep track of the names of built in functions/streams/reservered keywords so that the
algorithms in the srcmlparser FunctionCollector class doesn't confuse the names of certain srcml elements
with variable names in expression tags that are being parsed and collected. If they do get confused, it could
reduce the accuracy of the flow metric.
"""

C_LIB_FUNCTIONS = ('abort', 'abs', 'acos', 'asctime',
'asctime_r', 'asin', 'assert', 'atan',
'atan2', 'atexit', 'atof', 'atoi',
'atol', 'bsearch', 'btowc', 'calloc',
'catclose', 'catgets', 'catopen', 'ceil',
'clearerr', 'clock', 'cos', 'cosh',
'ctime', 'ctime64', 'ctime_r', 'ctime64_r',
'difftime', 'difftime64', 'div', 'erf',
'erfc', 'exit', 'exp', 'fabs',
'fclose', 'fdopen', 'feof', 'ferror',
'fflush', 'fgetc', 'fgetpos', 'fgets',
'fgetwc', 'fgetws', 'fileno', 'floor',
'fmod', 'fopen', 'fprintf', 'fputc',
'fputs', 'fputwc', 'fputws', 'fread',
'free', 'freopen', 'frexp', 'fscanf',
'fseek', 'fsetpos', 'ftell', 'fwide',
'fwprintf', 'fwrite', 'fwscanf', 'gamma',
'getc', 'getchar', 'getenv', 'gets',
'getwc', 'getwchar', 'gmtime', 'gmtime64',
'gmtime_r', 'gmtime64_r', 'hypot', 'isalnum',
'isalpha', 'isascii', 'isblank', 'iscntrl',
'isdigit', 'isgraph', 'islower', 'isprint',
'ispunct', 'isspace', 'isupper', 'iswalnum',
'iswalpha', 'iswblank', 'iswcntrl', 'iswctype',
'iswdigit', 'iswgraph', 'iswlower', 'iswprint',
'iswpunct', 'iswspace', 'iswupper', 'iswxdigit',
'isxdigit', 'j0', 'j1', 'jn',
'labs', 'ldexp', 'ldiv', 'localeconv',
'localtime', 'localtime64', 'localtime_r', 'localtime64_r',
'log', 'log10', 'longjmp', 'malloc',
'mblen', 'mbrlen', 'mbrtowc', 'mbsinit',
'mbsrtowcs', 'mbstowcs', 'mbtowc', 'memchr',
'memcmp', 'memcpy', 'memmove', 'memset',
'mktime', 'mktime64', 'modf', 'nextafter',
'nextafterl', 'nexttoward', 'nexttowardl', 'nl_langinfo',
'perror', 'pow', 'printf', 'putc',
'putchar', 'putenv', 'puts', 'putwc',
'putwchar', 'qsort', 'quantexpd32', 'quantexpd64',
'quantexpd128', 'quantized32', 'quantized64', 'quantized128',
'samequantumd32', 'samequantumd64', 'samequantumd128', 'raise',
'rand', 'rand_r', 'realloc', 'regcomp',
'regerror', 'regexec', 'regfree', 'remove',
'rename', 'rewind', 'scanf', 'setbuf',
'setjmp', 'setlocale', 'setvbuf', 'signal',
'sin', 'sinh', 'snprintf', 'sprintf',
'sqrt', 'srand', 'sscanf', 'strcasecmp',
'strcat', 'strchr', 'strcmp', 'strcoll',
'strcpy', 'strcspn', 'strerror', 'strfmon',
'strftime', 'strlen', 'strncasecmp', 'strncat',
'strncmp', 'strncpy', 'strpbrk', 'strptime',
'strrchr', 'strspn', 'strstr', 'strtod',
'strtod32', 'strtod64', 'strtod128', 'strtof',
'strtok', 'strtok_r', 'strtol', 'strtold',
'strtoul', 'strxfrm', 'swprintf', 'swscanf',
'system', 'tan', 'tanh', 'time',
'time64', 'tmpfile', 'tmpnam', 'toascii',
'tolower', 'toupper', 'towctrans', 'towlower',
'towupper', 'ungetc', 'ungetwc', 'va_arg',
'va_copy', 'va_end', 'va_start', 'vfprintf',
'vfscanf','vfwprintf', 'vfwscanf', 'vprintf',
'vscanf', 'vsprintf', 'vsnprintf', 'vsscanf',
'vswprintf', 'vswscanf', 'vwprintf', 'vwscanf',
'wcrtomb', 'wcscat', 'wcschr', 'wcscmp',
'wcscoll', 'wcscpy', 'wcscspn', 'wcsftime',
'wcslen', 'wcslocaleconv', 'wcsncat', 'wcsncmp',
'wcsncpy', 'wcspbrk', 'wcsptime', 'wcsrchr',
'char *ctime64_r(const time64_t *time, char *buf);',
'wcsspn', 'wcsstr', 'wcstod', 'wcstod32',
'wcstod64', 'wcstod128', 'wcstof', 'wcstok', 'wcstol',
'wcstold', 'wcstombs', 'wcstoul', 'wcsxfrm',
'wctob', 'wctomb', 'wctrans', 'wctype',
'wcwidth', 'wmemchr', 'wmemcmp', 'wmemcpy',
'wmemmove', 'wmemset', 'wprintf','wscanf',
'y0', 'y1', 'yn')

C_LIB_STREAMS = ("stderr", "stdout")

C_RESERVED_KEYWORDS = (
    "auto", "const", "int", "short", "struct",
    "unsigned", "double", "float", "break", "continue",
    "long", "signed", "switch", "void", "else", "for", "case",
    "default", "register", "sizeof", "typedef", "volatile",
    "enum", "goto", "char", "do", "return", "static",
    "union", "while", "extern", "if")

C_PLUS_PLUS_STDLIB_FUNCS = (
'abort', 'abs' ,'acos', 'asin',
'atan', 'atexit', 'atof', 'atoi',
'atol', 'ceil', 'clock', 'cosh',
'ctime', 'div', 'exit', 'fabs',
'floor', 'fmod', 'getchar', 'getenv',
'isalnum', 'isalpha', 'isdigit', 'isgraph',
'ispunct', 'isspace', 'isupper', 'kbhit',
'log10', 'log2', 'log', 'memcmp',
'modf', 'pow', 'putchar', 'putenv',
'puts', 'rand', 'remove', 'rename',
'sinh', 'sqrt', 'srand', 'strcat',
'strcmp', 'strerror', 'time', 'tolower',
'toupper',
)

C_PLUS_PLUS_RESERVED_KEYWORDS = (
    'alignas', 'alignof', 'and', 'and_eq',
    'asm', 'atomic_cancel', 'atomic_commit', 'atomic_noexcept',
    'auto', 'bitand', 'bitor', 'bool',
    'break', 'case', 'catch', 'char',
    'char8_t', 'char16_t', 'char32_t', 'class',
    'compl', 'concept', 'const', 'consteval',
    'constexpr', 'constinit', 'const_cast', 'continue',
    'co_await', 'co_return', 'co_yield', 'decltype',
    'default', 'delete', 'do', 'double',
    'dynamic_cast', 'else', 'enum', 'explicit',
    'export', 'extern', 'false', 'float',
    'for', 'friend', 'goto', 'if',
    'inline', 'int', 'long', 'mutable',
    'namespace', 'new', 'noexcept', 'not',
    'not_eq', 'nullptr', 'operator', 'or',
    'or_eq', 'private', 'protected', 'public',
    'reflexpr', 'register', 'reinterpret_cast', 'requires',
    'return', 'short', 'signed', 'sizeof',
    'static', 'static_assert', 'static_cast', 'struct',
    'switch', 'synchronized', 'template', 'this',
    'thread_local', 'throw', 'true', 'try',
    'typedef', 'typeid', 'typename', 'union',
    'unsigned', 'using (1)', 'virtual', 'void',
    'volatile', 'wchar_t', 'while', 'xor',
    'xor_eq')

C_PLUS_PLUS_STREAMS = (
'cin', 'cout', 'cerr', 'clog'
)

def _get_constants_from_language(language):
    if language == 'C':
        return (
            C_LIB_FUNCTIONS,
            C_LIB_STREAMS,
            C_RESERVED_KEYWORDS)
    elif language == 'C++':
        return (
            C_PLUS_PLUS_STDLIB_FUNCS,
            C_PLUS_PLUS_STREAMS,
            C_PLUS_PLUS_RESERVED_KEYWORDS)

    return (), (), ()
