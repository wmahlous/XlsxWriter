###############################################################################
#
# Worksheet - A class for writing Excel Worksheets.
#
# Copyright 2013, John McNamara, jmcnamara@cpan.org
#

import xmlwriter
from collections import defaultdict
from collections import namedtuple
from utility import xl_rowcol_to_cell


class Worksheet(xmlwriter.XMLwriter):
    """
    A class for writing Excel Worksheets.

    """

    ###########################################################################
    #
    # Public API.
    #
    ###########################################################################

    def __init__(self):
        """
        Constructor.

        """

        super(Worksheet, self).__init__()

        self.name = None
        self.index = None
        self.activesheet = None
        self.firstsheet = None
        self.str_total = None
        self.str_unique = None
        self.str_table = None
        self.table_count = None
        self.date_1904 = None
        self.palette = None
        self.optimization = 0
        self.tempdir = None

        self.ext_sheets = []
        self.fileclosed = 0
        self.excel_version = 2007

        self.xls_rowmax = 1048576
        self.xls_colmax = 16384
        self.xls_strmax = 32767
        self.dim_rowmin = None
        self.dim_rowmax = None
        self.dim_colmin = None
        self.dim_colmax = None

        self.colinfo = []
        self.selections = []
        self.hidden = 0
        self.active = 0
        self.tab_color = 0

        self.panes = []
        self.active_pane = 3
        self.selected = 0

        self.page_setup_changed = 0
        self.paper_size = 0
        self.orientation = 1

        self.print_options_changed = 0
        self.hcenter = 0
        self.vcenter = 0
        self.print_gridlines = 0
        self.screen_gridlines = 1
        self.print_headers = 0

        self.header_footer_changed = 0
        self.header = ''
        self.footer = ''

        self.margin_left = 0.7
        self.margin_right = 0.7
        self.margin_top = 0.75
        self.margin_bottom = 0.75
        self.margin_header = 0.3
        self.margin_footer = 0.3

        self.repeat_rows = ''
        self.repeat_cols = ''
        self.print_area = ''

        self.page_order = 0
        self.black_white = 0
        self.draft_quality = 0
        self.print_comments = 0
        self.page_start = 0

        self.fit_page = 0
        self.fit_width = 0
        self.fit_height = 0

        self.hbreaks = []
        self.vbreaks = []

        self.protect = 0
        self.password = None

        self.set_cols = {}
        self.set_rows = {}

        self.zoom = 100
        self.zoom_scale_normal = 1
        self.print_scale = 100
        self.right_to_left = 0
        self.show_zeros = 1
        self.leading_zeros = 0

        self.outline_row_level = 0
        self.outline_col_level = 0
        self.outline_style = 0
        self.outline_below = 1
        self.outline_right = 1
        self.outline_on = 1
        self.outline_changed = 0

        self.default_row_height = 15
        self.default_row_zeroed = 0

        self.names = {}
        self.write_match = []
        self.table = defaultdict(dict)
        self.merge = []
        self.row_spans = {}

        self.has_vml = 0
        self.has_comments = 0
        self.comments = {}
        self.comments_array = []
        self.comments_author = ''
        self.comments_visible = 0
        self.vml_shape_id = 1024
        self.buttons_array = []

        self.autofilter = ''
        self.filter_on = 0
        self.filter_range = []
        self.filter_cols = {}

        self.col_sizes = {}
        self.row_sizes = {}
        self.col_formats = {}
        self.col_size_changed = 0
        self.row_size_changed = 0

        self.last_shape_id = 1
        self.rel_count = 0
        self.hlink_count = 0
        self.hlink_refs = []
        self.external_hyper_links = []
        self.external_drawing_links = []
        self.external_comment_links = []
        self.external_vml_links = []
        self.external_table_links = []
        self.drawing_links = []
        self.charts = []
        self.images = []
        self.tables = []
        self.sparklines = []
        self.shapes = []
        self.shape_hash = {}
        self.drawing = 0

        self.rstring = ''
        self.previous_row = 0

        self.validations = []
        self.cond_formats = {}
        self.dxf_priority = 1

    def write_number(self, row, col, num, format=None):
        """
        Write a number to a worksheet cell.

        Args:
            row:    The cell row (zero indexed).
            col:    The cell column (zero indexed).
            num:    Cell data. Int or float.
            format: An optional Format object.

        Returns:
            0:  Success.
            -1: Column number is out of worksheet bounds.

        """
        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # TODO
        # Write previous row if in in-line string optimization mode.
        #if self.optimization == 1 and row > self.previous_row:
        #    self._write_single_row(row)

        cell_tuple = namedtuple('Number', 'number, format')
        self.table[row][col] = cell_tuple(num, format)

        return 0

    def select(self):
        """
        Set this worksheet as a selected worksheet, i.e. the worksheet
        has its tab highlighted.

        Note: A selected worksheet cannot be hidden.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.selected = 1
        self.hidden = 0

    def set_column(self, firstcol, lastcol, width,
                   format=None, hidden=False, level=0):
        """
        Set the width, and other properties of a single column or a
        range of columns.

        Args:
            firstcol: First column (zero-indexed).
            lastcol:  Last column (zero-indexed). Can be the same as firstcol.
            width:    Column width.
            format:   Column format. (optional).
            hidden:   Column is hidden. (default 0).
            level:    Column outline level. (default 0).

        Returns:
            0:  Success.
            -1: Column number is out of worksheet bounds.

        """
        # Ensure 2nd col is larger than first.
        if firstcol > lastcol:
            (firstcol, lastcol) = (lastcol, firstcol)

        # Don't modify the row dimensions when checking the columns.
        ignore_row = 1

        # Store the column dimension only in some conditions.
        if format or (width and hidden):
            ignore_col = 0
        else:
            ignore_col = 1

        # Check that each column is valid and store the max and min values.
        if self._check_dimensions(0, firstcol, ignore_row, ignore_col):
            return -1
        if self._check_dimensions(0, lastcol, ignore_row, ignore_col):
            return -1

        # Set the limits for the outline levels (0 <= x <= 7).
        if level is None:
            level = 0
        if level < 0:
            level = 0
        if level > 7:
            level = 7

        if level > self.outline_col_level:
            self.outline_col_level = level

        # Store the column data.
        self.colinfo.append([firstcol, lastcol, width, format, hidden, level])

        # Store the column change to allow optimisations.
        self.col_size_changed = 1

        # Store the col sizes for use when calculating image vertices taking
        # hidden columns into account. Also store the column formats.

        # Set width to zero if col is hidden
        if hidden:
            width = 0

        for col in range(firstcol, lastcol + 1):
            self.col_sizes[col] = width
            if format:
                self.col_formats[col] = format

        return 0

    ###########################################################################
    #
    # Private API.
    #
    ###########################################################################

    def _assemble_xml_file(self):
        # Assemble and write the XML file.

        # Write the XML declaration.
        self._xml_declaration()

        # Write the worksheet element.
        self._write_worksheet()

        # Write the dimension element.
        self._write_dimension()

        # Write the sheetViews element.
        self._write_sheet_views()

        # Write the sheetFormatPr element.
        self._write_sheet_format_pr()

        # Write the cols element.
        self._write_cols()

        # Write the sheetData element.
        self._write_sheet_data()

        # Write the pageMargins element.
        self._write_page_margins()

        # Close the worksheet tag.
        self._xml_end_tag('worksheet')

    def _check_dimensions(self, row, col, ignore_row=0, ignore_col=0):
        # Check that row and col are valid and store the max and min
        # values for use in other methods/elements. The ignore_row /
        # ignore_col flags is used to indicate that we wish to perform
        # the dimension check without storing the value. The ignore
        # flags are use by set_row() and data_validate.

        # Check that the row/col are within the worksheet bounds.
        if row >= self.xls_rowmax or col >= self.xls_colmax:
            return -1

        # In optimization mode we don't change dimensions for rows
        # that are already written.
        if not ignore_row and not ignore_col and self.optimization == 1:
            if row < self.previous_row:
                return -1

        if not ignore_row:
            if self.dim_rowmin is None or row < self.dim_rowmin:
                self.dim_rowmin = row
            if self.dim_rowmax is None or row > self.dim_rowmax:
                self.dim_rowmax = row

        if not ignore_col:
            if self.dim_colmin is None or col < self.dim_colmin:
                self.dim_colmin = col
            if self.dim_colmax is None or col > self.dim_colmax:
                self.dim_colmax = col

        return 0

    ###########################################################################
    #
    # XML methods.
    #
    ###########################################################################

    def _write_worksheet(self):
        # Write the <worksheet> element. This is the root element.

        schema = 'http://schemas.openxmlformats.org/'
        xmlns = schema + 'spreadsheetml/2006/main'
        xmlns_r = schema + 'officeDocument/2006/relationships'
        xmlns_mc = schema + 'markup-compatibility/2006'
        ms_schema = 'http://schemas.microsoft.com/'
        xmlns_mv = 'urn:schemas-microsoft-com:mac:vml'
        mc_ignorable = 'mv'
        mc_preserve_attributes = 'mv:*'

        attributes = [
            ('xmlns', xmlns),
            ('xmlns:r', xmlns_r),
        ]

        # Add some extra attributes for Excel 2010. Mainly for sparklines.
        if self.excel_version == 2010:
            attributes.append(('xmlns:mc',
                               schema + 'markup-compatibility/2006'))
            attributes.append(('xmlns:x14ac',
                               ms_schema + 'office/spreadsheetml/2009/9/ac'))
            attributes.append(('mc:Ignorable', 'x14ac'))

        self._xml_start_tag('worksheet', attributes)

    def _write_dimension(self):
        # Write the <dimension> element. This specifies the range of
        # cells in the worksheet. As a special case, empty
        # spreadsheets use 'A1' as a range.

        if self.dim_rowmin is None and self.dim_colmin is None:
            # If the min dimensions are not defined then no dimensions
            # have been set and we use the default 'A1'.
            ref = 'A1'

        elif self.dim_rowmin is None and self.dim_colmin is not None:
            # If the row dimensions aren't set but the column
            # dimensions are set then they have been changed via
            # set_column().

            if self.dim_colmin == self.dim_colmax:
                # The dimensions are a single cell and not a range.
                ref = xl_rowcol_to_cell(0, self.dim_colmin)
            else:
                # The dimensions are a cell range.
                cell_1 = xl_rowcol_to_cell(0, self.dim_colmin)
                cell_2 = xl_rowcol_to_cell(0, self.dim_colmax)
                ref = cell_1 + ':' + cell_2

        elif (self.dim_rowmin == self.dim_rowmax and
              self.dim_colmin == self.dim_colmax):
            # The dimensions are a single cell and not a range.
            ref = xl_rowcol_to_cell(self.dim_rowmin, self.dim_colmin)
        else:
            # The dimensions are a cell range.
            cell_1 = xl_rowcol_to_cell(self.dim_rowmin, self.dim_colmin)
            cell_2 = xl_rowcol_to_cell(self.dim_rowmax, self.dim_colmax)
            ref = cell_1 + ':' + cell_2

        self._xml_empty_tag('dimension', [('ref', ref)])

    def _write_sheet_views(self):
        # Write the <sheetViews> element.
        self._xml_start_tag('sheetViews')

        # Write the sheetView element.
        self._write_sheet_view()

        self._xml_end_tag('sheetViews')

    def _write_sheet_view(self):
        # Write the <sheetView> element.
        tab_selected = '1'
        workbook_view_id = '0'

        attributes = [
            ('tabSelected', tab_selected),
            ('workbookViewId', workbook_view_id),
        ]

        self._xml_empty_tag('sheetView', attributes)

    def _write_sheet_format_pr(self):
        # Write the <sheetFormatPr> element.
        default_row_height = '15'

        attributes = [('defaultRowHeight', default_row_height)]

        self._xml_empty_tag('sheetFormatPr', attributes)

    def _write_cols(self):
        # Write the <cols> element and <col> sub elements.

        # Exit unless some column have been formatted.
        if not self.colinfo:
            return

        self._xml_start_tag('cols')

        for col_info in (self.colinfo):
            self._write_col_info(col_info)

        self._xml_end_tag('cols')

    def _write_col_info(self, colinfo):
        # Write the <col> element.

        min, max, width, format, hidden, level = colinfo
        collapsed = 0
        custom_width = 1
        xf_index = 0

        # Get the format index.
        if format:
            xf_index = format._get_xf_index()

        # Set the Excel default col width.
        if width is None:
            if not hidden:
                width = 8.43
                custom_width = 0
            else:
                width = 0
        elif width == 8.43:
            # Width is defined but same as default.
            custom_width = 0

        # Convert column width from user units to character width.
        if width > 0:
             # For Calabri 11.
            max_digit_width = 7
            padding = 5
            width = int((float(width) * max_digit_width + padding)
                        / max_digit_width * 256.0) / 256.0

        attributes = [
            ('min', min + 1),
            ('max', max + 1),
            ('width', width),
        ]

        if xf_index:
            attributes.append(('style', xf_index))
        if hidden:
            attributes.append(('hidden', '1'))
        if custom_width:
            attributes.append(('customWidth', '1'))
        if level:
            attributes.append(('outlineLevel', level))
        if collapsed:
            attributes.append(('collapsed', '1'))

        self._xml_empty_tag('col', attributes)

    def _write_sheet_data(self):
        # Write the <sheetData> element.

        if self.dim_rowmin is None:
            # If the dimensions aren't defined there is no data to write.
            self._xml_empty_tag('sheetData')
        else:
            self._xml_start_tag('sheetData')
            self._write_rows()
            self._xml_end_tag('sheetData')

    def _write_page_margins(self):
        # Write the <pageMargins> element.
        left = '0.7'
        right = '0.7'
        top = '0.75'
        bottom = '0.75'
        header = '0.3'
        footer = '0.3'

        attributes = [
            ('left',   left),
            ('right',  right),
            ('top',    top),
            ('bottom', bottom),
            ('header', header),
            ('footer', footer),
        ]

        self._xml_empty_tag('pageMargins', attributes)

    def _write_rows(self):
        # Write out the worksheet data as a series of rows and cells.
        self._calculate_spans()

        for row_num in range(self.dim_rowmin, self.dim_rowmax + 1):

            if (row_num in self.set_rows or row_num in self.comments
                    or self.table[row_num]):
                # Only process rows that contain row formatting, cell
                # data comments.
                span_index = int(row_num / 16)
                span = self.row_spans[span_index]

                if self.table[row_num]:
                    # Write the cells if the row contains data.
                    if row_num not in self.set_rows:
                        self._write_row(row_num, span)
                    else:
                        self._write_row(row_num, span, self.set_rows[row_num])

                    for col_num in range(self.dim_colmin, self.dim_colmax + 1):
                        if self.table[row_num][col_num]:
                            col_ref = self.table[row_num][col_num]
                            self._write_cell(row_num, col_num, col_ref)

                    self._xml_end_tag('row')

                elif self.comments[row_num]:
                    # Row with comments in cells.
                    self._write_empty_row(row_num, span,
                                          self.set_rows[row_num])
                else:
                    # Blank row with attributes only.
                    self._write_empty_row(row_num, span,
                                          self.set_rows[row_num])

    def _calculate_spans(self):
        # Calculate the "spans" attribute of the <row> tag. This is an
        # XLSX optimisation and isn't strictly required. However, it
        # makes comparing files easier. The span is the same for each
        # block of 16 rows.
        spans = {}
        span_min = None
        span_max = None

        for row_num in range(self.dim_rowmin, self.dim_rowmax + 1):

            if row_num in self.table:
                # Calculate spans for cell data.
                for col_num in range(self.dim_colmin, self.dim_colmax + 1):
                    if col_num in self.table[row_num]:
                        if span_min is None:
                            span_min = col_num
                            span_max = col_num
                        else:
                            if col_num < span_min:
                                span_min = col_num
                            if col_num > span_max:
                                span_max = col_num

            if row_num in self.comments:
                # Calculate spans for comments.
                for col_num in range(self.dim_colmin, self.dim_colmax + 1):
                    if self.comments[row_num][col_num] is not None:

                        if span_min is None:
                            span_min = col_num
                            span_max = col_num
                        else:
                            if col_num < span_min:
                                span_min = col_num
                            if col_num > span_max:
                                span_max = col_num

            if ((row_num + 1) % 16 == 0) or row_num == self.dim_rowmax:
                span_index = int(row_num / 16)

                if span_min is not None:
                    span_min = span_min + 1
                    span_max = span_max + 1
                    spans[span_index] = "%s:%s" % (span_min, span_max)
                    span_min = None

        self.row_spans = spans

    def _write_row(self, r, spans, properties=None, empty_row=0):
        # Write the <row> element.
        xf_index = 0

        if properties:
            height, format, hidden, level, collapsed = properties
        else:
            height, format, hidden, level, collapsed = 15, None, 0, 0, 0

        if height is None:
            height = self.default_row_height

        attributes = [('r', r + 1)]

        # Get the format index.
        if format:
            xf_index = format._get_xf_index()

        # Add row attributes where applicable.
        if spans is not None:
            attributes.append(('spans', spans))
        if xf_index:
            attributes.append(('s', xf_index))
        if format:
            attributes.append(('customFormat', 1))
        if height != 15:
            attributes.append(('ht', height))
        if hidden:
            attributes.append(('hidden', 1))
        if height != 15:
            attributes.append(('customHeight', 1))
        if level:
            attributes.append(('outlineLevel', level))
        if collapsed:
            attributes.append(('collapsed', 1))
        if self.excel_version == 2010:
            attributes.append(('x14ac:dyDescent', '0.25'))

        if empty_row:
            self._xml_empty_tag_unencoded('row', attributes)
        else:
            self._xml_start_tag_unencoded('row', attributes)

    def _write_cell(self, row, col, cell):
        # Write the <cell> element.
        #
        # Note. This is the innermost loop so efficiency is important.
        range = xl_rowcol_to_cell(row, col)

        attributes = [('r', range)]

        # Add the cell format index.
        if cell.format:
            xf_index = cell.format._get_xf_index()
            attributes.append(('s', xf_index))
        elif row in self.set_rows and self.set_rows[row][1]:
            row_xf = self.set_rows[row][1]
            attributes.append(('s', row_xf._get_xf_index()))
        elif col in self.col_formats:
            col_xf = self.col_formats[col]
            attributes.append(('s', col_xf._get_xf_index()))

        # Write the various cell types.
        if type(cell).__name__ == 'Number':
            # Write a number.
            self._xml_number_element(cell.number, attributes)