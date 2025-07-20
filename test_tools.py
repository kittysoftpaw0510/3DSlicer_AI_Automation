from tools.app_3dslicer_tools import scroll_slice_up

def test_scroll_slices_coronal():
    """
    Test the scroll_slices_coronal tool by calling it with test parameters.
    This function prints the result for manual inspection.
    """
    # Use test parameters (host/port can be left as default if no Slicer server is running)
    result = scroll_slice_up()
    print("Test result for scroll_slices_coronal:", result)

if __name__ == "__main__":
    test_scroll_slices_coronal()