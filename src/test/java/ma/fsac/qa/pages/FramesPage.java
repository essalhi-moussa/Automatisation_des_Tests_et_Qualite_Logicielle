package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import java.time.Duration;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

/**
 * Formy ne contient aucune page avec iFrame : cette page appartient a the-internet.herokuapp.com
 * (/nested_frames) et sert uniquement a couvrir l'exigence "frames/iFrames" (frames imbriques).
 */
public class FramesPage extends BasePage {

    public FramesPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir la page nested_frames (the-internet)")
    public FramesPage open() {
        open(Config.iframeBaseUrl() + "/nested_frames");
        new WebDriverWait(driver, Duration.ofSeconds(45)).until(ExpectedConditions.presenceOfElementLocated(By.name("frame-top")));
        return this;
    }

    /** Lit le texte d'un frame du haut (left, middle, right) en traversant les deux niveaux. */
    @Step("Lire le texte du frame du haut : {position}")
    public String readTopFrame(String position) {
        driver.switchTo().defaultContent();
        new WebDriverWait(driver, Duration.ofSeconds(45)).until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(By.name("frame-top")));
        new WebDriverWait(driver, Duration.ofSeconds(45)).until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(By.name("frame-" + position)));
        String text = bodyText();
        driver.switchTo().defaultContent();
        return text;
    }

    @Step("Lire le texte du frame du bas")
    public String readBottomFrame() {
        driver.switchTo().defaultContent();
        new WebDriverWait(driver, Duration.ofSeconds(45)).until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(By.name("frame-bottom")));
        String text = bodyText();
        driver.switchTo().defaultContent();
        return text;
    }

    public int topFrameCount() {
        driver.switchTo().defaultContent();
        new WebDriverWait(driver, Duration.ofSeconds(45)).until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(By.name("frame-top")));
        new WebDriverWait(driver, Duration.ofSeconds(45)).until(ExpectedConditions.numberOfElementsToBe(By.tagName("frame"), 3));
        int n = driver.findElements(By.tagName("frame")).size();
        driver.switchTo().defaultContent();
        return n;
    }

    /** Texte brut du body courant (textContent : fiable meme si le body est tres petit). */
    private String bodyText() {
        // le serveur de demonstration est lent : attente dediee de 45 s ; on attend que le document du frame (et non le frameset parent) soit charge
        new WebDriverWait(driver, Duration.ofSeconds(45)).until(d -> Boolean.TRUE.equals(((JavascriptExecutor) d).executeScript(
                "return location.pathname.indexOf('/frame_') === 0 && document.readyState === 'complete';"))
                && !textContentOfBody(d).isBlank());
        return textContentOfBody(driver);
    }

    private static String textContentOfBody(WebDriver d) {
        Object v = ((JavascriptExecutor) d)
                .executeScript("return document.body ? document.body.textContent.trim() : '';");
        return v == null ? "" : v.toString();
    }
}
