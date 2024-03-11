from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotspareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file
    Saves the screenshot of the ordered robot
    Embeds the screenshot of the robot to the PDF receipt
    Creates ZIP archive of the receipts and the images
    """   
  
    open_robot_order_website()    
    download_orders_file() 
    close_annoying_modal()  
    fill_order_form()
    archive_receipts()   


def open_robot_order_website():
    """Opens the RobotSpareBin website and agrees to terms and conditions"""
    page = browser.page()
    page.goto("https://robotsparebinindustries.com/#/robot-order")
    

def close_annoying_modal():
    page = browser.page()   
    page.click("button:text('OK')")

def download_orders_file():
    """Downloads orders.csv file"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    

def get_orders():
    """Returns orders"""   
    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv", columns=["Order number","Head", "Body", "Legs", "Address"])    
    return orders

def fill_order_form():
    """Reads the downloaded CVS file as a table"""
    orders = get_orders()    
    for order in orders:
        fill_and_submit_order(order)

def fill_and_submit_order(robot_part):
    
    page = browser.page()
    #selecting the head
    page.select_option("#head", str(robot_part["Head"]))

    #selecting the body
    for i in range(1, 7):  
        if robot_part["Body"] == str(i):  
            page.check(f"#id-body-{i}")  

    #filling the legs field
    page.fill(".form-control", robot_part["Legs"])

    #filling the address field
    page.fill("#address", robot_part["Address"])
   
    page.click("button:text('PREVIEW')")      

    page.click("button:text('ORDER')") 

    if page.query_selector(".alert.alert-danger"):
        while page.query_selector(".alert.alert-danger"):
            page.click("button:text('ORDER')")


    store_receipt_as_pdf(robot_part["Order number"])
    screenshot_robot(robot_part["Order number"])
    embed_screenshot_to_receipt(screenshot_robot(robot_part["Order number"]), store_receipt_as_pdf(robot_part["Order number"]))
    page.click("button:text('ORDER ANOTHER ROBOT')")
    close_annoying_modal()  

    
def store_receipt_as_pdf(order_number):
    """Stores the receipt part of the confirmation page"""
    page = browser.page()
    order_receipt = page.locator("#order-completion").inner_html()
    pdf = PDF()
    
    pdf_path = f"output/receipts/order-number-{order_number}.pdf"
    pdf.html_to_pdf(order_receipt, pdf_path)
   
    return pdf_path

def screenshot_robot(order_number):
    """Takes a screenshot of the robot"""
    
    page = browser.page()

    element = page.locator("#robot-preview-image")
    screenshot_path = f"output/screenshots/robot-screenshot-{order_number}.png"
    element.screenshot(path=screenshot_path)
    
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Adds the screenshot of the robot to the appropriate PDF receipt"""

    pdf = PDF()
  
    print(f"PDF File Path: {pdf_file}")
    print(f"Screenshot Path: {screenshot}")
    pdf.open_pdf(pdf_file)
    pdf.add_files_to_pdf([screenshot], pdf_file,append=True)
  
    
def archive_receipts():
        """Zips the receipts folder"""    
        zip = Archive()
        zip.archive_folder_with_zip("output/receipts", "output/receipts.zip",)
    