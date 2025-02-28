def read_file(filename):
    """
    Returns content of a file as a string.

    Uses classic file access.
    """
    lines = []
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            lines = [line.strip().split(':') for line in lines]
    except FileNotFoundError:
        pass
    finally:
        return lines


def read_file_using_with(filename):
    """
    Returns content of a file as a string.

    Uses with statement to open a file.
    """

    lines = 'Unable to open a file: {0}'.format(filename)
    try:
        pass
    except FileNotFoundError:
        pass
    finally:
        return lines


def filter_cities(filename, **kw):
    """
    Returns a list of cities that match their population specified by restrictions.
    In **kw it will be possible to set an argument:
     'gt': only cities with a population greater than the value of the argument
     'lt': only cities with a population less than the value of the argument
    It is possible to enter none, one or both parameters at once.
    If no parameter is specified, an empty list is returned.
    Use list comprehension for filtering.
    Use so-called "unpacking" to load data.

    Reimplement the function to return a generator.
    """

    cities = read_file(filename)
    filtered = []
    if 'gt' in kw:
        filtered = [city for city in cities if int(city[1]) > kw['gt']]
    if 'lt' in kw:
        filtered = [city for city in cities if int(city[1]) < kw['lt']]

    return filtered


def main():
    """
    Main function.
    This function is run at the startup of a script thanks to the cryptic if statement below.
    """

    # file reading
    filename = 'mesta.txt'
    # content = read_file(filename)
    # print('{} file content is: {}'.format(filename, content))

    # content = read_file_using_with(filename)
    # print('{} file content using with statement is: {}'.format(filename, content))

    # filtering
    # print(filter_cities(filename, gt=500000))
    # print(filter_cities(filename, lt=300000))
    print(filter_cities(filename, lt=300000, gt=500000))


if __name__ == '__main__':
    main()