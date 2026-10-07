package ma.fsac.qa.base;

import ma.fsac.qa.listeners.TestListener;
import org.openqa.selenium.PageLoadStrategy;
import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Listeners;

/**
 * Classe de base des tests UI. Le WebDriver est stocke dans un ThreadLocal
 * afin de permettre l'execution parallele sans partage d'etat.
 */
@Listeners(TestListener.class)
public abstract class BaseTest {

    private static final ThreadLocal<WebDriver> DRIVER = new ThreadLocal<>();

    public static WebDriver getDriver() {
        return DRIVER.get();
    }

    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        DRIVER.set(DriverFactory.create(pageLoadStrategy()));
    }

    /** Strategie de chargement des pages ; surchargeable pour les pages tres lentes. */
    protected PageLoadStrategy pageLoadStrategy() {
        return PageLoadStrategy.EAGER;
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        WebDriver driver = DRIVER.get();
        if (driver != null) {
            driver.quit();
            DRIVER.remove();
        }
    }
}
