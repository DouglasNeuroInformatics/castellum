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
                onChange: onListSelectionChanged},
            this.props.children
        );
    }
}

class FormGroup extends React.Component {
    constructor(props) {
        super(props);

        this.state = {selectedTimeslots: this.props.selected};
        this.onCheckboxSelectionChanged = this.onCheckboxSelectionChanged.bind(this);
        this.onListSelectionChanged = this.onListSelectionChanged.bind(this);
    }

    onCheckboxSelectionChanged(selectedTimeslots) {
        this.setState({selectedTimeslots});
    }

    onListSelectionChanged(event) {
        const {options} = event.target;
        const selectedTimeslots = [...options].filter(o => o.selected).map(o => o.value);
        this.setState({selectedTimeslots});
    }

    render() {
        const selectorString = '[data-js="availability-timeslots"] div';
        const timeslots = [...document.querySelectorAll(selectorString)].map(t => t.textContent);

        return e('div', {className: 'form-group'}, [
            e(
                Checkbox,
                {
                    key: 'checkbox',
                    onSelectionChanged: this.onCheckboxSelectionChanged,
                    allTimeslots: timeslots,
                    selectedTimeslots: this.state.selectedTimeslots,
                },
                this.props.children
            ),
            e(
                Select,
                {
                    key: 'select',
                    selectedTimeslots: this.state.selectedTimeslots,
                    onListSelectionChanged: this.onListSelectionChanged,
                },
                timeslots.map(timeslot => e('option', {key: timeslot, value: timeslot}, timeslot))
            ),
        ]);
    }
}

class Availability extends React.Component {
    render() {
        const availability = document.querySelector('[data-js="availability-selected-timeslots"]');
        const weekdays = [...availability.querySelectorAll('[data-js="weekdays"] div')].map(wd => wd.textContent);

        return e(
            'div',
            {className: 'row', style: {width: '100%'}},
            weekdays.map(wd => e(
                'div',
                {key: wd, className: 'col-6 col-sm-2 mb-3'},
                e(
                    FormGroup,
                    {
                        selected: [...availability.querySelectorAll(`[data-js="selected"] [data-js="${wd}"] div`)].map(s => s.textContent),
                    },
                    wd
                ))
            )
        );
    }
}

const domContainer = document.querySelector('#availability');

ReactDOM.render(e(Availability), domContainer);
