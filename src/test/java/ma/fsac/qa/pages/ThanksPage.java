package ma.fsac.qa.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public class ThanksPage extends BasePage {

    public ThanksPage(WebDriver driver) {
        super(driver);
    }

    public String heading() {
        return textOf(By.tagName("h1"));
    }

    public String confirmationMessage() {
        return textOf(By.cssSelector(".alert.alert-success"));
    }
}
