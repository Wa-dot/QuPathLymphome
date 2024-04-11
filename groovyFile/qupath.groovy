public Item(Domain name)
    {
    _view = new ItemView(); 
    _view.get_Button().addClickListener(new SayHelloClickListener());
}

@Override
    public Component getView() {
        return _view;
    }

    public class SayHelloClickListener implements ClickListener {

        /* (non-Javadoc)
         * @see com.vaadin.ui.Button.ClickListener#buttonClick(com.vaadin.ui.Button.ClickEvent)
         */
        private static final long serialVersionUID = 1L;

        @Override
        public void buttonClick(ClickEvent event) {
            _view.getUI().addWindow(new Window("Title", contentComponent));
    }}