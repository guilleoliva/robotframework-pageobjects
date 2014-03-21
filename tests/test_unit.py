import os
from nose.tools import raises
from mock import patch
from robot.libraries.BuiltIn import BuiltIn
from unittest import skipUnless

from basetestcase import BaseTestCase
from robotpageobjects import exceptions
from robotpageobjects.page import Page, Override
from robotpageobjects.optionhandler import OptionHandler


class InheritFromSe2LibTestCase(BaseTestCase):

    def setUp(self):
        super(InheritFromSe2LibTestCase, self).setUp()

        class PO(Page):
            pass

        self.po = PO()

    def test_no_robot_se2lib_exposed(self):
        # We can't test this as a unittest in
        # robot, so see functional test class.

        try:
            getattr(self.po, "title_should_be")
        except AttributeError:
            self.fail("SE2Lib methods are not exposed as direct page object attributes")


class OptionHandlerTestCase(BaseTestCase):
    def test_is_singleton(self):
        ids = []
        for i in range(3):
            ids.append(id(OptionHandler()))
        self.assertTrue(all(x == ids[0] for x in ids), "All OptionHandler instances should refer to the same instance")

    def test_no_robot_get_env_var(self):
        os.environ["PO_FOO"] = "bar"
        handler = OptionHandler()
        self.assertEquals(handler.get("foo"), "bar")

    def test_no_robot_env_not_set_is_none(self):
        handler = OptionHandler()
        self.assertIsNone(handler.get("fasdfasdfasdfsadf"))

    @skipUnless(os.name == "posix", "Skipping Windows, since environment variables are not case sensitive")
    def test_no_robot_ignore_lowercase_env_vars(self):
        os.environ["PO_BROWSEr"] = "firefox"
        handler = OptionHandler()
        self.assertIsNone(handler.get("browser"), "Mixed case environment variables should not be set")

    @raises(exceptions.VarFileImportErrorError)
    def test_var_file_import_exception(self):
        os.environ["PO_VAR_FILE"] = "foo/bar/asdfsadf/asdf"
        handler = OptionHandler()
        handler.get("PO_VAR_FILE")

    def test_no_robot_var_file(self):
        os.environ["PO_VAR_FILE"] = "%s/vars.py" % self.test_dir
        handler = OptionHandler()
        self.assertEquals(handler.get("author"), "Dickens")
        self.assertEquals(handler.get("dynamic"), "Python")

    @patch.object(BuiltIn, "get_variables")
    def test_robot(self, mock_get_variables):
        mock_get_variables.return_value = {"${browser}": "foobar"}
        handler = OptionHandler()
        self.assertEquals(handler.get("browser"), "foobar")


class ResolveUrlTestCase(BaseTestCase):
    def setUp(self):
        super(ResolveUrlTestCase, self).setUp()

        class PO(Page):
            pass

        self.PO = PO

    ### Exceptions ###
    @raises(exceptions.NoBaseUrlError)
    def test_no_baseurl_set_no_uri_attr_set_should_raise_NoBaseUrlException(self):
        self.PO()._resolve_url()

    @raises(exceptions.NoBaseUrlError)
    def test_no_baseurl_set_no_uri_attr_set_uri_vars_set_should_raise_NoBaseUrlExeption(self):
        self.PO()._resolve_url("bar")

    @raises(exceptions.NoBaseUrlError)
    def test_no_baseurl_set_uri_attr_set_uri_vars_set_should_raise_NoBaseUrlExeption(self):
        self.PO.uri = "/foo"
        self.PO()._resolve_url("bar")

    @raises(exceptions.NoUriAttributeError)
    def test_baseurl_set_no_uri_attr_set_should_raise_NoUriAttributeException(self):
        self.set_baseurl_env()
        self.PO()._resolve_url()

    @raises(exceptions.AbsoluteUriAttributeError)
    def test_baseurl_set_abs_uri_attr_should_raise_AbsoulteUrlAttributeException(self):
        self.set_baseurl_env()
        self.PO.uri = "http://www.example.com"
        self.PO()._resolve_url()

    @raises(exceptions.AbsoluteUriTemplateError)
    def test_baseurl_set_abs_uri_template_should_raise_AbsoluteUriTemplateException(self):
        self.set_baseurl_env()
        self.PO.uri_template = "http://www.ncbi.nlm.nih.gov/pubmed/{pid}"
        print self.PO()._resolve_url({"pid": "123"})

    @raises(exceptions.InvalidUriTemplateVariableError)
    def test_baseurl_set_bad_vars_passed_to_uri_template(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        self.PO()._resolve_url({"foo": "bar"})

    @raises(exceptions.MissingSauceOptionError)
    def test_missing_sauce_username_should_raise_missing_sauce_error(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        os.environ["PO_SAUCE_USERNAME"] = "abc"
        self.PO.uri = "/foo"
        self.PO()

    ### Normative Cases ###
    def test_rel_uri_attr_set(self):
        self.set_baseurl_env()
        self.PO.uri = "/foo"
        po_inst = self.PO()
        url = po_inst._resolve_url()
        self.assertEquals(url, po_inst.baseurl + po_inst.uri)
        self.assertRegexpMatches(url, "file:///.+/foo$")

    def test_uri_vars_set(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        url = self.PO()._resolve_url({"pid": "123"})
        self.assertEquals("http://www.ncbi.nlm.nih.gov/pubmed/123", url)

    ### Selectors ##
    @raises(exceptions.DuplicateKeyError)
    def test_selectors_dup(self):
        class BaseFoo(object):
            selectors = {"foo": "foo"}

        class BaseBar(object):
            selectors = {"foo": "bar"}

        class FooBarPage(Page, BaseFoo, BaseBar):
            selectors = {"foo": "baz"}
        page = FooBarPage()

    def test_selectors_merge_override(self):
        class BaseFoo(object):
            selectors = {"foo": "foo"}

        class BaseBar(object):
            selectors = {"bar": "bar",
                          "baz": "cat"}

        class FooBarPage(Page, BaseFoo, BaseBar):
            selectors = {Override("baz"): "baz"}

        page = FooBarPage()
        selectors = page.selectors
        self.assertEqual(selectors.get("foo"), "foo", "Selectors should contain 'foo' from BaseFoo.")
        self.assertEqual(selectors.get("bar"), "bar", "Selectors should contain 'bar' from BaseBar.")
        self.assertEqual(selectors.get("baz"), "baz", "Selector 'baz' should be overridden in FooBarPage." )
