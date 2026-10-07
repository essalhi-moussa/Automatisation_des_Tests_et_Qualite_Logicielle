package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * Page autonome (URL data:) contenant un iFrame et un iFrame imbrique.
 * Elle garantit un test de frames deterministe, independant de tout serveur externe.
 */
public class LocalFramesPage extends BasePage {

    private static final String HTML = "<html><body><h1 id='titre'>Page parente</h1>"
            + "<iframe id='externe' srcdoc=\"<p id='texte'>Contenu externe</p>"
            + "<iframe id='interne' srcdoc='<p id=texte>Contenu imbrique</p>'></iframe>\"></iframe>"
            + "</body></html>";

    public LocalFramesPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir la page locale contenant des iFrames")
    public LocalFramesPage open() {
        String encoded = Base64.getEncoder().encodeToString(HTML.getBytes(StandardCharsets.UTF_8));
        open("data:text/html;base64," + encoded);
        visible(By.id("titre"));
        return this;
    }

    public String parentTitle() {
        driver.switchTo().defaultContent();
        return textOf(By.id("titre"));
    }

    @Step("Lire le texte de l iFrame externe")
    public String readOuterFrame() {
        driver.switchTo().defaultContent();
        wait.until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(By.id("externe")));
        String text = textOf(By.id("texte"));
        driver.switchTo().defaultContent();
        return text;
    }

    @Step("Lire le texte de l iFrame imbrique")
    public String readInnerFrame() {
        driver.switchTo().defaultContent();
        wait.until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(By.id("externe")));
        wait.until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(By.id("interne")));
        String text = textOf(By.id("texte"));
        driver.switchTo().defaultContent();
        return text;
    }
}
