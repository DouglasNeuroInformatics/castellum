from castellum.contacts.forms import SearchForm


def test_only_mail():
    search = 'test@example.com'
    form = SearchForm({'search': search})
    assert form.is_valid()
    assert form.cleaned_data == {
        'search': search,
        'search_terms': ['test@example.com'],
        'email': 'test@example.com',
    }


def test_full():
    search = 'test@example.com Shenavar Meier'
    form = SearchForm({'search': search})
    assert form.is_valid()
    assert form.cleaned_data == {
        'search': search,
        'search_terms': ['test@example.com', 'shenavar', 'meier'],
        'first_name': 'Shenavar',
        'last_name': 'Meier',
        'email': 'test@example.com',
    }


def test_email_with_single_namepart():
    search = 'test@example.com Eve'
    form = SearchForm({'search': search})
    assert form.is_valid()
    assert form.cleaned_data == {
        'search': search,
        'search_terms': ['test@example.com', 'eve'],
        'first_name': 'Eve',
        'email': 'test@example.com',
    }


def test_excessive_whitespace():
    search = 'Eve        Meier  '
    form = SearchForm({'search': search})
    assert form.is_valid()
    assert form.cleaned_data == {
        'search': search.strip(),
        'search_terms': ['eve', 'meier'],
        'first_name': 'Eve',
        'last_name': 'Meier',
    }


def test_only_first_name():
    search = 'Eve'
    form = SearchForm({'search': search})
    assert not form.is_valid()


def test_more_than_one_email():
    search = 'test@example.com second@example.com'
    form = SearchForm({'search': search})
    assert not form.is_valid()
