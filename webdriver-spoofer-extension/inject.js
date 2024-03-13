function overrideNavigatorProperty() {
    Object.defineProperty(navigator, 'webdriver', { value: false, configurable: false });
}
overrideNavigator();
