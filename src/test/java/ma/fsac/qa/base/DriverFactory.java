package ma.fsac.qa.base;

import java.time.Duration;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.PageLoadStrategy;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;

/**
 * Cree le WebDriver. Aucun chemin de driver n'est code en dur : Selenium Manager
 * telecharge et resout automatiquement chromedriver / geckodriver / msedgedriver.
 */
public final class DriverFactory {

    private DriverFactory() {
    }

    public static WebDriver create() {
        return create(PageLoadStrategy.EAGER);
    }

    public static WebDriver create(PageLoadStrategy strategy) {
        String browser = Config.get("browser").toLowerCase();
        boolean headless = Config.getBoolean("headless");
        String[] size = Config.get("window.size").split(",");
        String sizeArg = size[0].trim() + "," + size[1].trim();

        WebDriver driver;
        switch (browser) {
            case "firefox" -> {
                FirefoxOptions o = new FirefoxOptions();
                if (headless) {
                    o.addArguments("-headless");
                }
                driver = new FirefoxDriver(o);
            }
            case "edge" -> {
                EdgeOptions o = new EdgeOptions();
                if (headless) {
                    o.addArguments("--headless=new");
                }
                o.addArguments("--window-size=" + sizeArg);
                driver = new EdgeDriver(o);
            }
            default -> {
                ChromeOptions o = new ChromeOptions();
                if (headless) {
                    o.addArguments("--headless=new");
                }
                o.setPageLoadStrategy(strategy);
                o.addArguments("--window-size=" + sizeArg, "--no-sandbox",
                        "--disable-dev-shm-usage", "--disable-search-engine-choice-screen");
                driver = new ChromeDriver(o);
            }
        }
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(Config.getInt("timeout.page.load")));
        if (!headless) {
            driver.manage().window().maximize();
        }
        return driver;
    }
}
