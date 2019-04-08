'use strict';

const e = React.createElement;

class Checkbox extends React.Component {
    constructor(props) {
        super(props);
        const {allTimeslots, selectedTimeslots} = this.props;

        this.state = {checked: selectedTimeslots === allTimeslots};
        this.handleSelectionChange = this.handleSelectionChange.bind(this);
    }

    handleSelectionChange(event) {
        this.props.onSelectionChanged(event.target.checked ? this.props.allTimeslots : []);
    }

    render() {
        return e('div', {className: 'form-check'}, [
            e(
                'input',
                {
                    key: 'input',
                    className: 'form-check-input',
                    type: 'checkbox',
                    onChange: this.handleSelectionChange,
                    checked: this.state.checked
                }
            ),
            e('label', {key: 'label', className: 'form-check-label'}, this.props.children),
        ]);
    };

    componentWillReceiveProps(nextProps) {
        const {allTimeslots} = this.props;
        const {selectedTimeslots} = nextProps;

        const checked = JSON.stringify(selectedTimeslots) === JSON.stringify(allTimeslots)
        this.setState({checked});
    }
}

class Select extends React.Component {
    render() {
        const {onListSelectionChanged, selectedTimeslots} = this.props;

        return e('select',
            {className: 'form-control', multiple: {}, value: selectedTimeslots,
                onChange: onListSelectionChanged,
                name: `availability_${this.props.name.toLowerCase()}`,
            },
            this.props.children
        );
    }
}

class FormGroup extends React.Component {
    constructor(props) {
        super(props);

        this.state = {selectedTimeslots: this.props.selectedTimeslots};
        this.onCheckboxSelectionChanged = this.onCheckboxSelectionChanged.bind(this);
        this.onListSelectionChanged = this.onListSelectionChanged.bind(this);
    }

    onCheckboxSelectionChanged(selectedTimeslots) {
        this.setState({selectedTimeslots});
    }

    onListSelectionChanged(event) {
        const {options} = event.target;
        const {allTimeslots} = this.props;
        const selectedTimeslots = [...options].filter(o => o.selected).map(o => (
            allTimeslots[o.value - 1]));
        this.setState({selectedTimeslots});
    }

    render() {
        const {allTimeslots, selectedTimeslots} = this.props;

        return e('div', {className: 'form-group'}, [
            e(Checkbox, {
                    key: 'checkbox',
                    onSelectionChanged: this.onCheckboxSelectionChanged,
                    allTimeslots: allTimeslots,
                    selectedTimeslots: this.state.selectedTimeslots,
                },
                this.props.children
            ),
            e(Select, {
                    key: 'select',
                    selectedTimeslots: this.state.selectedTimeslots.map(i => (
                        i - allTimeslots.length + 1)),
                    onListSelectionChanged: this.onListSelectionChanged,
                    name: this.props.children,
                },
                allTimeslots.map((ts, idx) => e('option', {key: idx, value: idx+1}, ts))
            ),
        ]);
    }
}

class Availability extends React.Component {
    render() {
        const selectorString = '[data-js="availability-timeslots"] div';
        const timeslots = [...document.querySelectorAll(selectorString)].map(t => t.textContent);

        const availability = document.querySelector('[data-js="availability-selected-timeslots"]');
        const weekdays = [...availability.querySelectorAll('[data-js="weekdays"] div')].map(wd => wd.textContent);

        return e(React.Fragment, {}, weekdays.map(wd => e(
            'div',
            {key: wd, className: 'col-6 col-sm-2 mb-3'},
            e(FormGroup, {
                allTimeslots: timeslots,
                selectedTimeslots: [...availability.querySelectorAll(`[data-js="selected"] [data-js="${wd}"] div`)].map(s => s.textContent),
            },
            wd)))
        );
    }
}

const domContainer = document.querySelector('#availability');

ReactDOM.render(e(Availability), domContainer);
