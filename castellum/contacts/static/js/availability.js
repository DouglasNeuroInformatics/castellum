'use strict';

const e = React.createElement;

const HOURS = [9, 10, 11, 12, 13, 14, 15, 16, 17];

class Checkbox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {checked: this.props.selectedHours === HOURS};
        this.handleSelectionChange = this.handleSelectionChange.bind(this);
    }

    handleSelectionChange(event) {
        this.props.onSelectionChanged(event.target.checked ? HOURS : []);
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
        const checked = JSON.stringify(nextProps.selectedHours) === JSON.stringify(HOURS)
        this.setState({checked});
    }
}

class FormGroup extends React.Component {
    constructor(props) {
        super(props);
        this.state = {selectedHours: []};
        this.onCheckboxSelectionChanged = this.onCheckboxSelectionChanged.bind(this);
        this.onListSelectionChanged = this.onListSelectionChanged.bind(this);
    }

    onCheckboxSelectionChanged(selectedHours) {
        this.setState({selectedHours});
    }

    onListSelectionChanged(event) {
        const {options} = event.target;
        const selectedHours = [...options].filter(o => o.selected).map(o => parseInt(o.value));
        this.setState({selectedHours});
    }

    render() {
        return e('div', {className: 'form-group'}, [
            e(
                Checkbox,
                {
                    key: 'checkbox',
                    onSelectionChanged: this.onCheckboxSelectionChanged,
                    selectedHours: this.state.selectedHours,
                },
                this.props.children
            ),
            e(
                'select',
                {
                    key: 'select',
                    className: 'form-control',
                    multiple: {},
                    value: this.state.selectedHours,
                    onChange: this.onListSelectionChanged,
                },
                HOURS.map(hour => e('option', {key: hour, value: hour}, hour))
            ),
        ]);
    }
}

class Availability extends React.Component {
    render() {
        const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

        return e(
            'div',
            {className: 'row', style: {width: '100%'}},
            weekdays.map(wd => e(
                'div',
                {key: wd, className: 'col-6 col-sm-2 mb-3'},
                e(FormGroup, {}, wd))
            )
        );
    }
}

const domContainer = document.querySelector('#availability');

ReactDOM.render(e(Availability), domContainer);
