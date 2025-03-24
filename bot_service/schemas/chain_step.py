from typing import Optional

from pydantic import BaseModel, model_validator


class ChainStepCreate(BaseModel):
    chain_id: int
    name: str
    message: str
    set_as_next_step_for_button_id: Optional[int] = None
    is_first_step_of_chain: bool = False
    next_step_id: Optional[int] = None
    text_input: bool = False

    @model_validator(mode="after")
    def validate_first_step_or_previous_button(self):
        is_first_step_of_chain = self.is_first_step_of_chain
        set_as_next_step_for_button_id = self.set_as_next_step_for_button_id

        if (
            is_first_step_of_chain is True
            and set_as_next_step_for_button_id is not None
        ) or (
            is_first_step_of_chain is False
            and set_as_next_step_for_button_id is None
        ):
            raise ValueError(
                "You must provide either 'is_first_step_of_chain=True' or 'set_as_next_step_for_button_id', but not both."
            )
        return self


class ChainStepUpdate(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None
    next_step_id: Optional[int] = None
    text_input: Optional[bool] = None


class ChainStepResponse(BaseModel):
    id: int
    chain_id: int
    name: str
    message: str
    next_step_id: Optional[int]
    text_input: bool
